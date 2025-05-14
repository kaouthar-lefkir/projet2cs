from rest_framework_simplejwt.tokens import RefreshToken
from .models import Projet, Phase, Operation,Seuil
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def update_project_costs(project_id):
    """
    Met à jour le coût actuel d'un projet en fonction des coûts de ses phases
    """
    try:
        projet = Projet.objects.get(pk=project_id)
        
        # Calcul du coût total des phases
        cout_phases = projet.phases.aggregate(total=Sum('cout_actuel'))['total'] or Decimal('0.00')
        
        # Mise à jour du coût actuel du projet
        projet.cout_actuel = cout_phases
        projet.save(update_fields=['cout_actuel'])
        
        return True
    except Projet.DoesNotExist:
        return False


def update_phase_costs(phase_id):
    """
    Met à jour le coût actuel d'une phase en fonction des coûts de ses opérations
    """
    try:
        phase = Phase.objects.get(pk=phase_id)
        
        # Calcul du coût total des opérations
        cout_operations = phase.operations.aggregate(total=Sum('cout_reel'))['total'] or Decimal('0.00')
        
        # Mise à jour du coût actuel de la phase
        phase.cout_actuel = cout_operations
        phase.save(update_fields=['cout_actuel'])
        
        # Mise à jour du coût du projet parent
        update_project_costs(phase.projet.id)
        
        return True
    except Phase.DoesNotExist:
        return False


    
def evaluer_statut_couleur_operation(operation, seuil=None):
    """
    Évalue le statut couleur (vert/jaune/rouge) d'une opération 
    en fonction de ses seuils et valeurs actuelles.
    
    Args:
        operation: L'objet Operation à évaluer
        seuil: L'objet Seuil associé (optionnel, sera récupéré si non fourni)
        
    Returns:
        Un dictionnaire contenant:
        - statut_cout: Le statut couleur pour le coût ('VERT', 'JAUNE', 'ROUGE')
        - statut_delai: Le statut couleur pour le délai ('VERT', 'JAUNE', 'ROUGE')
        - statut_global: Le statut couleur global (le plus grave des deux)
    """
    if not seuil:
        # Essayer de récupérer le seuil associé à cette opération
        try:
            seuil = operation.seuils.first()
        except:
            # Pas de seuil défini, on retourne tout en vert par défaut
            return {
                'statut_cout': 'VERT',
                'statut_delai': 'VERT',
                'statut_global': 'VERT'
            }
    
    # Vérifier que le seuil possède les attributs nécessaires
    if seuil is None or not hasattr(seuil, 'valeur_verte') or not hasattr(seuil, 'valeur_jaune'):
        # Si le seuil n'a pas les attributs nécessaires, retourner tout en vert par défaut
        return {
            'statut_cout': 'VERT',
            'statut_delai': 'VERT',
            'statut_global': 'VERT'
        }
    
    # Initialiser les statuts
    statut_cout = 'VERT'
    statut_delai = 'VERT'
    
    # Évaluer le statut pour le coût
    if operation.cout_reel is not None and operation.cout_prevue is not None and operation.cout_prevue > 0:
        pourcentage_cout = (operation.cout_reel / operation.cout_prevue) * 100
        
        if pourcentage_cout <= seuil.valeur_verte:
            statut_cout = 'VERT'
        elif pourcentage_cout <= seuil.valeur_jaune:
            statut_cout = 'JAUNE'
        else:
            statut_cout = 'ROUGE'
    
    # Évaluer le statut pour le délai
    if (operation.date_debut_reelle and operation.date_fin_prevue and 
        operation.date_fin_reelle is None):  # L'opération est en cours
        
        aujourd_hui = timezone.now().date()
        duree_totale = (operation.date_fin_prevue - operation.date_debut_prevue).days
        
        if duree_totale > 0:
            duree_ecoulee = (aujourd_hui - operation.date_debut_reelle).days
            pourcentage_temps_ecoule = (duree_ecoulee / duree_totale) * 100
            pourcentage_progression = operation.progression
            
            # Si la progression est en retard par rapport au temps écoulé
            ecart_progression = pourcentage_temps_ecoule - pourcentage_progression
            
            if ecart_progression <= seuil.valeur_verte:
                statut_delai = 'VERT'
            elif ecart_progression <= seuil.valeur_jaune:
                statut_delai = 'JAUNE'
            else:
                statut_delai = 'ROUGE'
    
    elif operation.date_fin_reelle and operation.date_fin_prevue:  # L'opération est terminée
        # Calculer le dépassement de délai
        retard = (operation.date_fin_reelle - operation.date_fin_prevue).days
        duree_prevue = (operation.date_fin_prevue - operation.date_debut_prevue).days
        
        if duree_prevue > 0:
            pourcentage_retard = (retard / duree_prevue) * 100
            
            if pourcentage_retard <= seuil.valeur_verte:
                statut_delai = 'VERT'
            elif pourcentage_retard <= seuil.valeur_jaune:
                statut_delai = 'JAUNE'
            else:
                statut_delai = 'ROUGE'
    
    # Déterminer le statut global (le plus grave des deux)
    statut_global = 'VERT'
    if statut_cout == 'ROUGE' or statut_delai == 'ROUGE':
        statut_global = 'ROUGE'
    elif statut_cout == 'JAUNE' or statut_delai == 'JAUNE':
        statut_global = 'JAUNE'
    
    return {
        'statut_cout': statut_cout,
        'statut_delai': statut_delai,
        'statut_global': statut_global
    }

def creer_alerte_seuil(operation, statut_precedent, statut_actuel):
    """
    Crée une alerte si le statut couleur d'une opération change vers un état plus critique
    
    Args:
        operation: L'objet Operation concerné
        statut_precedent: Le statut couleur précédent ('VERT', 'JAUNE', 'ROUGE')
        statut_actuel: Le statut couleur actuel ('VERT', 'JAUNE', 'ROUGE')
        
    Returns:
        L'objet Alerte créé ou None si aucune alerte n'a été créée
    """
    from .models import Alerte
    
    # Ordre de criticité
    ordre_criticite = {
        'VERT': 1,
        'JAUNE': 2,
        'ROUGE': 3
    }
    
    # Si le statut devient plus critique ou passe en rouge, créer une alerte
    if (ordre_criticite.get(statut_actuel, 0) > ordre_criticite.get(statut_precedent, 0) or 
        statut_actuel == 'ROUGE'):
        
        # Déterminer le niveau d'alerte
        niveau = 'INFO'
        if statut_actuel == 'JAUNE':
            niveau = 'WARNING'
        elif statut_actuel == 'ROUGE':
            niveau = 'CRITIQUE'
        
        # Créer l'alerte
        with transaction.atomic():
            alerte = Alerte.objects.create(
                projet=operation.phase.projet,
                phase=operation.phase,
                operation=operation,
                type_alerte='DEPASSEMENT_SEUIL',
                niveau=niveau,
                message=f"L'opération {operation.nom} a atteint un statut {statut_actuel}",
                statut='NON_LU'
            )
            return alerte
    
    return None


def calculate_project_progress(project_id):
    """
    Calcule la progression globale d'un projet basée sur la progression de ses phases
    
    Args:
        project_id: L'identifiant du projet
        
    Returns:
        La progression calculée (valeur entre 0 et 100)
    """
    from django.db.models import Avg
    from .models import Projet, Phase
    
    try:
        projet = Projet.objects.get(pk=project_id)
        phases = projet.phases.all()
        
        if not phases.exists():
            return 0
        
        # Si toutes les phases ont un budget défini, on utilise une moyenne pondérée par budget
        phases_with_budget = phases.exclude(budget_alloue__isnull=True).exclude(budget_alloue=0)
        if phases_with_budget.count() == phases.count():
            # Moyenne pondérée par le budget
            total_budget = sum(phase.budget_alloue for phase in phases)
            if total_budget > 0:
                progress = sum((phase.progression * phase.budget_alloue) for phase in phases) / total_budget
                return round(progress, 2)
        
        # Sinon, utiliser une moyenne simple
        progress = phases.aggregate(avg_progress=Avg('progression'))['avg_progress'] or 0
        return round(progress, 2)
    except Projet.DoesNotExist:
        return 0

def evaluer_statut_couleur_phase(phase):
    """
    Évalue le statut couleur (vert/jaune/rouge) d'une phase
    en agrégeant les statuts de ses opérations
    
    Args:
        phase: L'objet Phase à évaluer
        
    Returns:
        Un dictionnaire contenant:
        - statut_cout: Le statut couleur pour le coût ('VERT', 'JAUNE', 'ROUGE')
        - statut_delai: Le statut couleur pour le délai ('VERT', 'JAUNE', 'ROUGE')
        - statut_global: Le statut couleur global (le plus grave des deux)
    """
    from .models import Operation
    
    # Récupérer toutes les opérations de la phase
    operations = phase.operations.all()
    
    if not operations:
        return {
            'statut_cout': 'VERT',
            'statut_delai': 'VERT',
            'statut_global': 'VERT'
        }
    
    # Compter le nombre d'opérations par statut pour le coût
    cout_rouge = 0
    cout_jaune = 0
    cout_vert = 0
    
    # Compter le nombre d'opérations par statut pour le délai
    delai_rouge = 0
    delai_jaune = 0
    delai_vert = 0
    
    # Évaluer chaque opération
    for operation in operations:
        statut = evaluer_statut_couleur_operation(operation)
        
        # Comptage pour le coût
        if statut['statut_cout'] == 'ROUGE':
            cout_rouge += 1
        elif statut['statut_cout'] == 'JAUNE':
            cout_jaune += 1
        else:
            cout_vert += 1
        
        # Comptage pour le délai
        if statut['statut_delai'] == 'ROUGE':
            delai_rouge += 1
        elif statut['statut_delai'] == 'JAUNE':
            delai_jaune += 1
        else:
            delai_vert += 1
    
    # Déterminer le statut global pour le coût
    statut_cout = 'VERT'
    if cout_rouge > 0:
        statut_cout = 'ROUGE'
    elif cout_jaune > 0:
        statut_cout = 'JAUNE'
    
    # Déterminer le statut global pour le délai
    statut_delai = 'VERT'
    if delai_rouge > 0:
        statut_delai = 'ROUGE'
    elif delai_jaune > 0:
        statut_delai = 'JAUNE'
    
    # Déterminer le statut global (le plus grave des deux)
    statut_global = 'VERT'
    if statut_cout == 'ROUGE' or statut_delai == 'ROUGE':
        statut_global = 'ROUGE'
    elif statut_cout == 'JAUNE' or statut_delai == 'JAUNE':
        statut_global = 'JAUNE'
    
    return {
        'statut_cout': statut_cout,
        'statut_delai': statut_delai,
        'statut_global': statut_global
    }

def evaluer_statut_couleur_projet(projet):
    """
    Évalue le statut couleur (vert/jaune/rouge) d'un projet
    en agrégeant les statuts de ses phases
    
    Args:
        projet: L'objet Projet à évaluer
        
    Returns:
        Un dictionnaire contenant:
        - statut_cout: Le statut couleur pour le coût ('VERT', 'JAUNE', 'ROUGE')
        - statut_delai: Le statut couleur pour le délai ('VERT', 'JAUNE', 'ROUGE')
        - statut_global: Le statut couleur global (le plus grave des deux)
    """
    # Récupérer toutes les phases du projet
    phases = projet.phases.all()
    
    if not phases:
        return {
            'statut_cout': 'VERT',
            'statut_delai': 'VERT',
            'statut_global': 'VERT'
        }
    
    # Compter le nombre de phases par statut pour le coût
    cout_rouge = 0
    cout_jaune = 0
    cout_vert = 0
    
    # Compter le nombre de phases par statut pour le délai
    delai_rouge = 0
    delai_jaune = 0
    delai_vert = 0
    
    # Évaluer chaque phase
    for phase in phases:
        statut = evaluer_statut_couleur_phase(phase)
        
        # Comptage pour le coût
        if statut['statut_cout'] == 'ROUGE':
            cout_rouge += 1
        elif statut['statut_cout'] == 'JAUNE':
            cout_jaune += 1
        else:
            cout_vert += 1
        
        # Comptage pour le délai
        if statut['statut_delai'] == 'ROUGE':
            delai_rouge += 1
        elif statut['statut_delai'] == 'JAUNE':
            delai_jaune += 1
        else:
            delai_vert += 1
    
    # Déterminer le statut global pour le coût
    statut_cout = 'VERT'
    if cout_rouge > 0:
        statut_cout = 'ROUGE'
    elif cout_jaune > 0:
        statut_cout = 'JAUNE'
    
    # Déterminer le statut global pour le délai
    statut_delai = 'VERT'
    if delai_rouge > 0:
        statut_delai = 'ROUGE'
    elif delai_jaune > 0:
        statut_delai = 'JAUNE'
    
    # Déterminer le statut global (le plus grave des deux)
    statut_global = 'VERT'
    if statut_cout == 'ROUGE' or statut_delai == 'ROUGE':
        statut_global = 'ROUGE'
    elif statut_cout == 'JAUNE' or statut_delai == 'JAUNE':
        statut_global = 'JAUNE'
    
    return {
        'statut_cout': statut_cout,
        'statut_delai': statut_delai,
        'statut_global': statut_global
    }


def calculate_phase_progress(phase_id):
    """
    Calcule la progression d'une phase basée sur la progression de ses opérations
    
    Args:
        phase_id: L'identifiant de la phase
        
    Returns:
        La progression calculée (valeur entre 0 et 100)
    """
    from django.db.models import Avg, Count
    from .models import Phase, Operation
    
    try:
        phase = Phase.objects.get(pk=phase_id)
        operations = phase.operations.all()
        
        if not operations.exists():
            return 0
        
        # Si toutes les opérations ont un budget défini, on utilise une moyenne pondérée par budget
        operations_with_budget = operations.exclude(cout_prevue__isnull=True).exclude(cout_prevue=0)
        if operations_with_budget.count() == operations.count():
            # Moyenne pondérée par le budget
            total_budget = sum(op.cout_prevue for op in operations)
            if total_budget > 0:
                progress = sum((op.progression * op.cout_prevue) for op in operations) / total_budget
                return round(progress, 2)
        
        # Sinon, utiliser une moyenne simple
        progress = operations.aggregate(avg_progress=Avg('progression'))['avg_progress'] or 0
        return round(progress, 2)
    except Phase.DoesNotExist:
        return 0
    

def update_phase_progress(phase_id):
    """
    Met à jour la progression d'une phase en fonction de ses opérations
    
    Args:
        phase_id: L'identifiant de la phase
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    from .models import Phase
    
    try:
        phase = Phase.objects.get(pk=phase_id)
        
        # Calculer la progression
        progression = calculate_phase_progress(phase_id)
        
        # Mettre à jour la phase avec le flag skip_update pour éviter la récursion
        phase.progression = progression
        phase.save(update_fields=['progression'], skip_update=True)
        
        return True
    except Phase.DoesNotExist:
        return False


    
def update_project_progress(project_id):
    """
    Met à jour la progression d'un projet en fonction de ses phases
    
    Args:
        project_id: L'identifiant du projet
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    # Note: Comme le modèle Projet n'a pas de champ progression,
    # cette fonction ne fait que calculer la valeur sans la persister
    # Elle pourrait être utilisée dans des sérialiseurs ou des vues
    progression = calculate_project_progress(project_id)
    return progression > 0  # Retourne True si la progression a pu être calculée