from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DurationField, Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from ..models import (
    Projet, Phase, Operation, Utilisateur, 
    Probleme, EquipeProjet, Alerte
)
from .serializers import (
    DashboardGeneralSerializer, ResponsableProjectCountSerializer,
    ProjetDashboardSerializer, PhaseDashboardSerializer, OperationDashboardSerializer,
    IndicateursPerformanceSerializer, IndicateursEquipeSerializer, StatistiquesEquipeProjetSerializer
)
from ..utils import (
    evaluer_statut_couleur_projet, evaluer_statut_couleur_phase,
    evaluer_statut_couleur_operation, calculate_project_progress
)

class DashboardGeneralView(APIView):
    """
    Vue pour le tableau de bord général montrant les statistiques globales
    """
    def get(self, request):
        # Comptage des projets par statut
        total_projets = Projet.objects.count()
        projets_planifies = Projet.objects.filter(statut='PLANIFIE').count()
        projets_en_cours = Projet.objects.filter(statut='EN_COURS').count()
        projets_termines = Projet.objects.filter(statut='TERMINE').count()
        projets_suspendus = Projet.objects.filter(statut='SUSPENDU').count()
        
        # Budget global
        budget_initial_total = Projet.objects.aggregate(Sum('budget_initial'))['budget_initial__sum'] or Decimal('0.00')
        cout_actuel_total = Projet.objects.aggregate(Sum('cout_actuel'))['cout_actuel__sum'] or Decimal('0.00')
        ecart_budgetaire = cout_actuel_total - budget_initial_total
        
        # Délais
        today = timezone.now().date()
        projets_en_retard = Projet.objects.filter(
            date_fin_prevue__lt=today,
            date_fin_reelle__isnull=True,
            statut='EN_COURS'
        ).count()
        
        # Calcul du retard moyen pour les projets terminés en retard
        projets_termines_retard = Projet.objects.filter(
            date_fin_reelle__gt=F('date_fin_prevue'),
            statut='TERMINE'
        ).annotate(
            retard=ExpressionWrapper(
                F('date_fin_reelle') - F('date_fin_prevue'),
                output_field=DurationField()
            )
        )
        
        if projets_termines_retard.exists():
            retard_moyen_jours = projets_termines_retard.aggregate(
                avg_retard=Avg('retard')
            )['avg_retard'].days
        else:
            retard_moyen_jours = 0
        
        # Progression moyenne des projets
        projets_avec_phases = Projet.objects.filter(phases__isnull=False).only('id')
        if projets_avec_phases.exists():
            progression_moyenne = 0
            for projet in projets_avec_phases:
                progression_moyenne += calculate_project_progress(projet.id)
            progression_moyenne = progression_moyenne / projets_avec_phases.count()
        else:
            progression_moyenne = 0
        
        # Taux de réussite (projets terminés dans les délais et le budget)
        if projets_termines > 0:
            projets_reussis = Projet.objects.filter(
                statut='TERMINE',
                date_fin_reelle__lte=F('date_fin_prevue'),
                cout_actuel__lte=F('budget_initial')
            ).count()
            taux_reussite = (projets_reussis / projets_termines) * 100
        else:
            taux_reussite = 0
        
        data = {
            'total_projets': total_projets,
            'projets_planifies': projets_planifies,
            'projets_en_cours': projets_en_cours,
            'projets_termines': projets_termines,
            'projets_suspendus': projets_suspendus,
            'budget_initial_total': budget_initial_total,
            'cout_actuel_total': cout_actuel_total,
            'ecart_budgetaire': ecart_budgetaire,
            'projets_en_retard': projets_en_retard,
            'retard_moyen_jours': retard_moyen_jours,
            'progression_moyenne': progression_moyenne,
            'taux_reussite': taux_reussite
        }
        
        serializer = DashboardGeneralSerializer(data)
        return Response(serializer.data)


class IndicateurPerformanceGeneralView(APIView):
    """
    Vue pour les indicateurs de performance globaux
    """
    def get(self, request):
        # Filtrer les projets actifs (planifiés ou en cours)
        projets_actifs = Projet.objects.filter(statut__in=['PLANIFIE', 'EN_COURS'])
        
        # Efficacité (Progression moyenne / Pourcentage de temps écoulé)
        efficacite = 0
        projets_avec_progression = 0
        
        for projet in projets_actifs:
            if projet.date_debut and projet.date_fin_prevue:
                aujourd_hui = timezone.now().date()
                
                # Ne calculer que pour les projets déjà commencés
                if aujourd_hui >= projet.date_debut:
                    duree_totale = (projet.date_fin_prevue - projet.date_debut).days
                    if duree_totale > 0:
                        temps_ecoule = min((aujourd_hui - projet.date_debut).days, duree_totale)
                        pourcentage_temps_ecoule = (temps_ecoule / duree_totale) * 100
                        
                        progression = calculate_project_progress(projet.id)
                        
                        if pourcentage_temps_ecoule > 0:
                            rapport_efficacite = float(progression) / pourcentage_temps_ecoule
                            efficacite += rapport_efficacite
                            projets_avec_progression += 1
        
        if projets_avec_progression > 0:
            efficacite = efficacite / projets_avec_progression
        
        # Productivité coût (Travail réalisé / Coût)
        operations_terminees = Operation.objects.filter(statut='TERMINE', cout_reel__gt=0)
        
        if operations_terminees.exists():
            total_cout_operations = operations_terminees.aggregate(Sum('cout_reel'))['cout_reel__sum'] or Decimal('0.00')
            if total_cout_operations > 0:
                productivite_cout = operations_terminees.count() / total_cout_operations
            else:
                productivite_cout = Decimal('0.00')
        else:
            productivite_cout = Decimal('0.00')
        
        # Productivité temps (Nombre d'opérations terminées / Temps total)
        operations_avec_dates = Operation.objects.filter(
            statut='TERMINE',
            date_debut_reelle__isnull=False,
            date_fin_reelle__isnull=False
        )
        
        if operations_avec_dates.exists():
            total_jours = 0
            for op in operations_avec_dates:
                duree = (op.date_fin_reelle - op.date_debut_reelle).days
                total_jours += max(duree, 1)  # Au moins 1 jour par opération
            
            productivite_temps = operations_avec_dates.count() / total_jours if total_jours > 0 else 0
        else:
            productivite_temps = 0
        
        # Qualité (Nombre de problèmes par opération)
        total_operations = Operation.objects.count()
        total_problemes = Probleme.objects.count()
        
        if total_operations > 0:
            qualite_problemes = total_problemes / total_operations
        else:
            qualite_problemes = 0
        
        # Temps de résolution moyen des problèmes
        problemes_resolus = Probleme.objects.filter(
            statut='RESOLU',
            date_signalement__isnull=False,
            date_resolution__isnull=False
        )
        
        if problemes_resolus.exists():
            temps_resolution_total = 0
            for probleme in problemes_resolus:
                duree = (probleme.date_resolution - probleme.date_signalement).total_seconds() / 86400  # en jours
                temps_resolution_total += duree
            
            temps_resolution_moyen = temps_resolution_total / problemes_resolus.count()
        else:
            temps_resolution_moyen = 0
        
        data = {
            'efficacite': efficacite,
            'productivite_cout': productivite_cout,
            'productivite_temps': productivite_temps,
            'qualite_problemes': qualite_problemes,
            'temps_resolution_moyen': temps_resolution_moyen
        }
        
        serializer = IndicateursPerformanceSerializer(data)
        return Response(serializer.data)


class ProjetParResponsableView(APIView):
    """
    Vue pour obtenir la répartition des projets par responsable
    """
    def get(self, request):
        responsables_projets = []
        
        # Récupérer les responsables qui ont des projets assignés
        responsables = Utilisateur.objects.filter(projets_responsable__isnull=False).distinct()
        
        for responsable in responsables:
            nombre_projets = Projet.objects.filter(responsable=responsable).count()
            
            data = {
                'responsable_id': responsable.id,
                'responsable_nom': f"{responsable.prenom} {responsable.nom}",
                'nombre_projets': nombre_projets
            }
            
            serializer = ResponsableProjectCountSerializer(data=data)
            if serializer.is_valid():
                responsables_projets.append(serializer.data)
        
        return Response(responsables_projets)


class IndicateurEquipeView(APIView):
    """
    Vue pour obtenir les indicateurs sur les équipes des projets
    """
    def get(self, request):
        projet_id = request.query_params.get('projet_id', None)
        
        if projet_id:
            # Récupérer l'équipe pour un projet spécifique
            membres_equipe = EquipeProjet.objects.filter(projet_id=projet_id)
            
            # Statistiques générales de l'équipe
            nombre_membres = membres_equipe.count()
            
            # Compter par rôle
            ingenieur_terrain = 0
            expert = 0
            top_management = 0
            
            for membre in membres_equipe:
                if membre.utilisateur.role == 'INGENIEUR_TERRAIN':
                    ingenieur_terrain += 1
                elif membre.utilisateur.role == 'EXPERT':
                    expert += 1
                elif membre.utilisateur.role == 'TOP_MANAGEMENT':
                    top_management += 1
            
            stats_equipe = {
                'nombre_membres': nombre_membres,
                'ingenieur_terrain': ingenieur_terrain,
                'expert': expert,
                'top_management': top_management
            }
            
            stats_serializer = StatistiquesEquipeProjetSerializer(stats_equipe)
            
            # Détails par membre d'équipe
            indicateurs_membres = []
            
            for membre in membres_equipe:
                # Opérations assignées à ce membre
                operations_assignees = Operation.objects.filter(
                    responsable=membre.utilisateur,
                    phase__projet_id=projet_id
                )
                
                nombre_operations = operations_assignees.count()
                
                # Progression moyenne des opérations assignées
                if nombre_operations > 0:
                    progression_moyenne = operations_assignees.aggregate(
                        avg_prog=Avg('progression')
                    )['avg_prog'] or 0
                else:
                    progression_moyenne = 0
                
                data = {
                    'id': membre.utilisateur.id,
                    'nom_complet': membre.utilisateur.get_full_name(),
                    'role_projet': membre.role_projet,
                    'operations_assignees': nombre_operations,
                    'progression_moyenne': progression_moyenne
                }
                
                serializer = IndicateursEquipeSerializer(data)
                indicateurs_membres.append(serializer.data)
            
            # Retourner les deux ensembles de données
            return Response({
                'statistiques_generales': stats_serializer.data,
                'indicateurs_membres': indicateurs_membres
            })
        else:
            return Response(
                {"error": "Un ID de projet est requis pour cette vue"},
                status=status.HTTP_400_BAD_REQUEST
            )


class AlertesRecentesView(APIView):
    """
    Vue pour obtenir les alertes récentes (non lues ou récemment créées)
    """
    def get(self, request):
        # Nombre d'alertes à récupérer
        limit = int(request.query_params.get('limit', 10))
        projet_id = request.query_params.get('projet_id', None)
        
        # Filtrer par projet si spécifié
        if projet_id:
            alertes = Alerte.objects.filter(projet_id=projet_id)
        else:
            alertes = Alerte.objects.all()
        
        # Récupérer d'abord les alertes non lues
        alertes_non_lues = alertes.filter(statut='NON_LU')
        
        # Puis les alertes récentes (7 derniers jours)
        une_semaine = timezone.now() - timedelta(days=7)
        alertes_recentes = alertes.filter(date_alerte__gte=une_semaine)
        
        # Combiner et limiter
        alertes_combine = (alertes_non_lues | alertes_recentes).distinct().order_by('-date_alerte')[:limit]
        
        # Sérialiser les résultats
        result = []
        for alerte in alertes_combine:
            # Déterminer le contexte de l'alerte
            contexte = ""
            if alerte.operation:
                contexte = f"Opération: {alerte.operation.nom}"
            elif alerte.phase:
                contexte = f"Phase: {alerte.phase.nom}"
            elif alerte.projet:
                contexte = f"Projet: {alerte.projet.nom}"
            
            alerte_data = {
                'id': alerte.id,
                'type': alerte.type_alerte,
                'niveau': alerte.niveau,
                'message': alerte.message,
                'date': alerte.date_alerte,
                'statut': alerte.statut,
                'contexte': contexte,
                'projet_id': alerte.projet.id if alerte.projet else None,
                'phase_id': alerte.phase.id if alerte.phase else None,
                'operation_id': alerte.operation.id if alerte.operation else None
            }
            result.append(alerte_data)
        
        return Response(result)


class ProblemesRecentsView(APIView):
    """
    Vue pour obtenir les problèmes récents ou non résolus
    """
    def get(self, request):
        # Nombre de problèmes à récupérer
        limit = int(request.query_params.get('limit', 10))
        projet_id = request.query_params.get('projet_id', None)
        
        # Filtrer par projet si spécifié
        if projet_id:
            problemes = Probleme.objects.filter(
                Q(projet_id=projet_id) | 
                Q(phase__projet_id=projet_id) | 
                Q(operation__phase__projet_id=projet_id)
            )
        else:
            problemes = Probleme.objects.all()
        
        # Problèmes non résolus (statut OUVERT ou EN_COURS)
        problemes_non_resolus = problemes.filter(statut__in=['OUVERT', 'EN_COURS'])
        
        # Problèmes récents (30 derniers jours)
        un_mois = timezone.now() - timedelta(days=30)
        problemes_recents = problemes.filter(date_signalement__gte=un_mois)
        
        # Combiner et limiter
        problemes_combine = (problemes_non_resolus | problemes_recents).distinct().order_by('-date_signalement')[:limit]
        
        # Sérialiser les résultats
        result = []
        for probleme in problemes_combine:
            # Déterminer le contexte du problème
            contexte = ""
            if probleme.operation:
                contexte = f"Opération: {probleme.operation.nom}"
            elif probleme.phase:
                contexte = f"Phase: {probleme.phase.nom}"
            elif probleme.projet:
                contexte = f"Projet: {probleme.projet.nom}"
            
            # Compter les solutions proposées
            nb_solutions = probleme.solutions.count()
            
            probleme_data = {
                'id': probleme.id,
                'titre': probleme.titre,
                'description': probleme.description,
                'gravite': probleme.gravite,
                'statut': probleme.statut,
                'date_signalement': probleme.date_signalement,
                'contexte': contexte,
                'projet_id': probleme.projet.id if probleme.projet else None,
                'phase_id': probleme.phase.id if probleme.phase else None,
                'operation_id': probleme.operation.id if probleme.operation else None,
                'nb_solutions': nb_solutions
            }
            result.append(probleme_data)
        
        return Response(result)


class ProjetDashboardView(APIView):
    """
    Vue pour le tableau de bord d'un projet spécifique
    """
    def get(self, request, projet_id):
        try:
            projet = Projet.objects.get(pk=projet_id)
        except Projet.DoesNotExist:
            return Response(
                {"error": "Le projet spécifié n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Progression du projet
        progression = calculate_project_progress(projet_id)
        
        # Statut couleur du projet
        statut_couleur = evaluer_statut_couleur_projet(projet)
        
        # Budget
        budget_initial = projet.budget_initial or Decimal('0.00')
        cout_actuel = projet.cout_actuel or Decimal('0.00')
        
        if budget_initial > 0:
            pourcentage_budget_consomme = (cout_actuel / budget_initial) * 100
        else:
            pourcentage_budget_consomme = 0
        
        # Délais
        today = timezone.now().date()
        retard_jours = 0
        retard_pourcentage = 0
        
        if projet.date_fin_prevue:
            if projet.date_fin_reelle:
                # Projet terminé, calcul du retard réel
                retard_jours = max(0, (projet.date_fin_reelle - projet.date_fin_prevue).days)
            elif today > projet.date_fin_prevue:
                # Projet en cours et en retard
                retard_jours = (today - projet.date_fin_prevue).days
            
            # Calculer le pourcentage de retard par rapport à la durée prévue
            if projet.date_debut:
                duree_prevue = (projet.date_fin_prevue - projet.date_debut).days
                if duree_prevue > 0:
                    retard_pourcentage = (retard_jours / duree_prevue) * 100
        
        # Risques (alertes et problèmes)
        alertes_critiques = Alerte.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            niveau='CRITIQUE'
        ).count()
        
        alertes_avertissements = Alerte.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            niveau='WARNING'
        ).count()
        
        alertes_informations = Alerte.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            niveau='INFO'
        ).count()
        
        problemes_non_resolus_critiques = Probleme.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            statut__in=['OUVERT', 'EN_COURS'],
            gravite='CRITIQUE'
        ).count()
        
        problemes_non_resolus_eleves = Probleme.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            statut__in=['OUVERT', 'EN_COURS'],
            gravite='ELEVEE'
        ).count()
        
        problemes_non_resolus_moyens = Probleme.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            statut__in=['OUVERT', 'EN_COURS'],
            gravite='MOYENNE'
        ).count()
        
        problemes_non_resolus_faibles = Probleme.objects.filter(
            Q(projet=projet) | Q(phase__projet=projet) | Q(operation__phase__projet=projet),
            statut__in=['OUVERT', 'EN_COURS'],
            gravite='FAIBLE'
        ).count()
        
        # Préparer les données pour le sérialiseur
        data = {
            'id': projet.id,
            'nom': projet.nom,
            'progression': progression,
            'statut_cout': statut_couleur['statut_cout'],
            'statut_delai': statut_couleur['statut_delai'],
            'statut_global': statut_couleur['statut_global'],
            'budget_initial': budget_initial,
            'cout_actuel': cout_actuel,
            'pourcentage_budget_consomme': pourcentage_budget_consomme,
            'date_debut': projet.date_debut,
            'date_fin_prevue': projet.date_fin_prevue,
            'date_fin_reelle': projet.date_fin_reelle,
            'retard_jours': retard_jours,
            'retard_pourcentage': retard_pourcentage,
            'alertes_critiques': alertes_critiques,
            'alertes_avertissements': alertes_avertissements,
            'alertes_informations': alertes_informations,
            'problemes_non_resolus_critiques': problemes_non_resolus_critiques,
            'problemes_non_resolus_eleves': problemes_non_resolus_eleves,
            'problemes_non_resolus_moyens': problemes_non_resolus_moyens,
            'problemes_non_resolus_faibles': problemes_non_resolus_faibles
        }
        
        serializer = ProjetDashboardSerializer(data)
        return Response(serializer.data)


class PhaseDashboardView(APIView):
    """
    Vue pour le tableau de bord d'une phase
    """
    def get(self, request, phase_id):
        try:
            phase = Phase.objects.get(id=phase_id)
        except Phase.DoesNotExist:
            return Response({"error": "Phase non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        
        # Progression
        progression = float(phase.progression) if phase.progression is not None else 0.0
        
        # Utiliser la fonction d'évaluation du statut couleur depuis les utils
        statut_couleur = evaluer_statut_couleur_phase(phase)
        
        # Budget et coût
        budget_alloue = phase.budget_alloue or Decimal('0.00')
        
        # Calcul du coût actuel de la phase (somme des coûts réels des opérations)
        operations = Operation.objects.filter(phase=phase)
        cout_actuel = operations.aggregate(Sum('cout_reel'))['cout_reel__sum'] or Decimal('0.00')
        
        # Calcul du pourcentage de budget consommé
        pourcentage_budget_consomme = 0
        if budget_alloue > 0:
            pourcentage_budget_consomme = float(cout_actuel / budget_alloue) * 100
        
        # Calcul du retard
        retard_jours = 0
        aujourd_hui = timezone.now().date()
        
        if phase.date_fin_prevue and phase.date_fin_reelle:
            retard_jours = (phase.date_fin_reelle - phase.date_fin_prevue).days
        elif phase.date_fin_prevue and phase.date_fin_prevue < aujourd_hui and phase.statut != 'TERMINE':
            retard_jours = (aujourd_hui - phase.date_fin_prevue).days
        
        # Comptage des opérations
        operations = Operation.objects.filter(phase=phase)
        operations_terminees = operations.filter(statut='TERMINE').count()
        operations_en_cours = operations.filter(statut='EN_COURS').count()
        operations_planifiees = operations.filter(statut='PLANIFIE').count()
        operations_suspendues = operations.filter(statut='SUSPENDU').count()
        
        # Calcul du pourcentage d'opérations en retard
        operations_retard = 0
        total_operations_avec_date = 0
        
        for op in operations.exclude(statut='TERMINE'):
            if op.date_fin_prevue and op.date_fin_prevue < aujourd_hui:
                operations_retard += 1
            if op.date_fin_prevue:
                total_operations_avec_date += 1
        
        pourcentage_operations_retard = 0
        if total_operations_avec_date > 0:
            pourcentage_operations_retard = (operations_retard / total_operations_avec_date) * 100
        
        # Structure des données
        data = {
            'id': phase.id,
            'nom': phase.nom,
            'progression': progression,
            
            # Utiliser les valeurs de statut de la fonction d'évaluation
            'statut_cout': statut_couleur['statut_cout'].lower(),  # Convertir en minuscules pour cohérence
            'statut_delai': statut_couleur['statut_delai'].lower(),
            'statut_global': statut_couleur['statut_global'].lower(),
            
            'budget_alloue': budget_alloue,
            'cout_actuel': cout_actuel,
            'pourcentage_budget_consomme': pourcentage_budget_consomme,
            
            'date_debut_prevue': phase.date_debut_prevue,
            'date_fin_prevue': phase.date_fin_prevue,
            'date_debut_reelle': phase.date_debut_reelle,
            'date_fin_reelle': phase.date_fin_reelle,
            'retard_jours': retard_jours,
            
            'operations_terminees': operations_terminees,
            'operations_en_cours': operations_en_cours,
            'operations_planifiees': operations_planifiees,
            'operations_suspendues': operations_suspendues,
            'pourcentage_operations_retard': pourcentage_operations_retard
        }
        
        serializer = PhaseDashboardSerializer(data)
        return Response(serializer.data)
    
class OperationDashboardView(APIView):
    """
    Vue pour le tableau de bord d'une opération spécifique
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, operation_id):
        aujourd_hui = timezone.now().date()
        
        try:
            operation = Operation.objects.get(id=operation_id)
        except Operation.DoesNotExist:
            return Response(
                {"detail": "Opération non trouvée."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser la fonction evaluer_statut_couleur_operation du fichier utils
        statuts = evaluer_statut_couleur_operation(operation)
        
        # Récupérer les statuts depuis le résultat de la fonction
        statut_cout = statuts['statut_cout'].capitalize()  # Convertir 'VERT' en 'Vert'
        statut_delai = statuts['statut_delai'].capitalize()
        statut_global = statuts['statut_global'].capitalize()
        
        # Calcul du retard en jours
        retard_jours = 0
        if operation.date_fin_reelle and operation.date_fin_prevue:
            # Si l'opération est terminée, calculer le retard réel
            if operation.date_fin_reelle > operation.date_fin_prevue:
                retard_jours = (operation.date_fin_reelle - operation.date_fin_prevue).days
        elif operation.date_fin_prevue and aujourd_hui > operation.date_fin_prevue:
            # Si l'opération n'est pas terminée et la date prévue est dépassée
            retard_jours = (aujourd_hui - operation.date_fin_prevue).days
        
        
        # Calcul de l'écart de coût
        ecart_cout = operation.cout_reel - operation.cout_prevue
        if operation.cout_prevue > 0:
            pourcentage_ecart_cout = (ecart_cout / operation.cout_prevue) * 100
        else:
            pourcentage_ecart_cout = 0
        
        # Comptage des problèmes associés
        problemes_ouverts = Probleme.objects.filter(
            operation=operation, 
            statut='Ouvert'
        ).count()
        
        problemes_en_cours = Probleme.objects.filter(
            operation=operation, 
            statut='En cours'
        ).count()
        
        problemes_resolus = Probleme.objects.filter(
            operation=operation, 
            statut='Résolu'
        ).count()
        
        # Création du dictionnaire de données pour le sérialiseur
        operation_data = {
            'id': operation.id,
            'nom': operation.nom,
            'progression': operation.progression,
            
            # Statut couleur (provenant de la fonction evaluer_statut_couleur_operation)
            'statut_cout': statut_cout,
            'statut_delai': statut_delai,
            'statut_global': statut_global,
            
            # Coût
            'cout_prevue': operation.cout_prevue,
            'cout_reel': operation.cout_reel,
            'ecart_cout': ecart_cout,
            'pourcentage_ecart_cout': pourcentage_ecart_cout,
            
            # Délais
            'date_debut_prevue': operation.date_debut_prevue,
            'date_fin_prevue': operation.date_fin_prevue,
            'date_debut_reelle': operation.date_debut_reelle,
            'date_fin_reelle': operation.date_fin_reelle,
            'retard_jours': retard_jours,
            
            # Problèmes
            'problemes_ouverts': problemes_ouverts,
            'problemes_en_cours': problemes_en_cours,
            'problemes_resolus': problemes_resolus,
        }
        
        serializer = OperationDashboardSerializer(data=operation_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)