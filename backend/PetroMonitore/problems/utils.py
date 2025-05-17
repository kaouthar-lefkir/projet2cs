from django.utils import timezone
from ..models import HistoriqueModification, Probleme

def track_probleme_status_change(probleme_id, old_status, new_status, user=None):
    """
    Enregistre un changement de statut de problème dans l'historique des modifications
    
    Args:
        probleme_id (int): ID du problème
        old_status (str): Ancien statut
        new_status (str): Nouveau statut
        user (Utilisateur): Utilisateur qui effectue la modification
    """
    probleme = Probleme.objects.get(id=probleme_id)
    
    # Créer une entrée dans l'historique des modifications
    HistoriqueModification.objects.create(
        table_modifiee='Probleme',
        id_enregistrement=probleme_id,
        champ_modifie='statut',
        ancienne_valeur=old_status,
        nouvelle_valeur=new_status,
        date_modification=timezone.now(),
        modifie_par=user,
        commentaire=f"Changement de statut du problème '{probleme.titre}'"
    )
    
    return True


def track_solution_status_change(solution_id, old_status, new_status, user=None):
    """
    Enregistre un changement de statut de solution dans l'historique des modifications
    
    Args:
        solution_id (int): ID de la solution
        old_status (str): Ancien statut
        new_status (str): Nouveau statut
        user (Utilisateur): Utilisateur qui effectue la modification
    """
    from ..models import Solution
    solution = Solution.objects.get(id=solution_id)
    
    # Créer une entrée dans l'historique des modifications
    HistoriqueModification.objects.create(
        table_modifiee='Solution',
        id_enregistrement=solution_id,
        champ_modifie='statut',
        ancienne_valeur=old_status,
        nouvelle_valeur=new_status,
        date_modification=timezone.now(),
        modifie_par=user,
        commentaire=f"Changement de statut d'une solution pour le problème '{solution.probleme.titre}'"
    )
    
    # Si la solution passe à MISE_EN_OEUVRE, mettre à jour le statut du problème associé si nécessaire
    if new_status == 'MISE_EN_OEUVRE' and solution.probleme.statut not in ['RESOLU', 'FERME']:
        old_probleme_status = solution.probleme.statut
        solution.probleme.statut = 'EN_COURS'
        solution.probleme.save()
        
        # Enregistrer aussi le changement de statut du problème
        track_probleme_status_change(
            solution.probleme.id, 
            old_probleme_status, 
            'EN_COURS', 
            user
        )
    
    return True


def get_probleme_statistics(projet_id=None, phase_id=None):
    """
    Retourne des statistiques sur les problèmes
    
    Args:
        projet_id (int, optional): ID du projet pour filtrer
        phase_id (int, optional): ID de la phase pour filtrer
        
    Returns:
        dict: Statistiques des problèmes
    """
    from django.db.models import Count
    
    # Construire le filtre de base
    filter_kwargs = {}
    if projet_id:
        filter_kwargs['projet_id'] = projet_id
    if phase_id:
        filter_kwargs['phase_id'] = phase_id
    
    # Récupérer les données
    problemes = Probleme.objects.filter(**filter_kwargs)
    
    # Compter par statut
    statut_counts = problemes.values('statut').annotate(count=Count('id'))
    status_stats = {item['statut']: item['count'] for item in statut_counts}
    
    # Compter par gravité
    gravite_counts = problemes.values('gravite').annotate(count=Count('id'))
    gravite_stats = {item['gravite']: item['count'] for item in gravite_counts}
    
    # Compter le total
    total = problemes.count()
    
    # Calculer les pourcentages de résolution
    resolved = status_stats.get('RESOLU', 0) + status_stats.get('FERME', 0)
    resolution_rate = (resolved / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'par_statut': status_stats,
        'par_gravite': gravite_stats,
        'taux_resolution': round(resolution_rate, 2)
    }