from rest_framework import serializers
from ..models import Projet, Phase, Operation, Utilisateur, Probleme, EquipeProjet, Alerte
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone
from decimal import Decimal


class DashboardGeneralSerializer(serializers.Serializer):
    """
    Sérialiseur pour le tableau de bord général montrant les statistiques globales
    """
    # Comptage des projets
    total_projets = serializers.IntegerField()
    projets_planifies = serializers.IntegerField()
    projets_en_cours = serializers.IntegerField()
    projets_termines = serializers.IntegerField()
    projets_suspendus = serializers.IntegerField()
    
    # Budget global
    budget_initial_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    cout_actuel_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    ecart_budgetaire = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Délais
    projets_en_retard = serializers.IntegerField()
    retard_moyen_jours = serializers.FloatField()
    
    # Progression
    progression_moyenne = serializers.FloatField()
    
    # Taux de réussite
    taux_reussite = serializers.FloatField()


class ResponsableProjectCountSerializer(serializers.Serializer):
    """
    Sérialiseur pour les comptages de projets par responsable
    """
    responsable_id = serializers.IntegerField()
    responsable_nom = serializers.CharField()
    nombre_projets = serializers.IntegerField()


class ProjetDashboardSerializer(serializers.Serializer):
    """
    Sérialiseur pour les données du tableau de bord d'un projet spécifique
    """
    id = serializers.IntegerField()
    nom = serializers.CharField()
    progression = serializers.FloatField()
    
    # Statut couleur
    statut_cout = serializers.CharField()
    statut_delai = serializers.CharField()
    statut_global = serializers.CharField()
    
    # Budget
    budget_initial = serializers.DecimalField(max_digits=15, decimal_places=2)
    cout_actuel = serializers.DecimalField(max_digits=15, decimal_places=2)
    pourcentage_budget_consomme = serializers.FloatField()
    
    # Délais
    date_debut = serializers.DateField()
    date_fin_prevue = serializers.DateField()
    date_fin_reelle = serializers.DateField(allow_null=True)
    retard_jours = serializers.IntegerField()
    retard_pourcentage = serializers.FloatField()
    
    # Risques
    alertes_critiques = serializers.IntegerField()
    alertes_avertissements = serializers.IntegerField()
    alertes_informations = serializers.IntegerField()
    problemes_non_resolus_critiques = serializers.IntegerField()
    problemes_non_resolus_eleves = serializers.IntegerField()
    problemes_non_resolus_moyens = serializers.IntegerField()
    problemes_non_resolus_faibles = serializers.IntegerField()


class PhaseDashboardSerializer(serializers.Serializer):
    """
    Sérialiseur pour les données du tableau de bord d'une phase spécifique
    """
    id = serializers.IntegerField()
    nom = serializers.CharField()
    progression = serializers.FloatField()
    
    # Statut couleur
    statut_cout = serializers.CharField()
    statut_delai = serializers.CharField()
    statut_global = serializers.CharField()
    
    # Budget
    budget_alloue = serializers.DecimalField(max_digits=15, decimal_places=2)
    cout_actuel = serializers.DecimalField(max_digits=15, decimal_places=2)
    pourcentage_budget_consomme = serializers.FloatField()
    
    # Délais
    date_debut_prevue = serializers.DateField()
    date_fin_prevue = serializers.DateField()
    date_debut_reelle = serializers.DateField(allow_null=True)
    date_fin_reelle = serializers.DateField(allow_null=True)
    retard_jours = serializers.IntegerField()
    
    # Opérations
    operations_terminees = serializers.IntegerField()
    operations_en_cours = serializers.IntegerField()
    operations_planifiees = serializers.IntegerField()
    operations_suspendues = serializers.IntegerField()
    pourcentage_operations_retard = serializers.FloatField()


class OperationDashboardSerializer(serializers.Serializer):
    """
    Sérialiseur pour les données du tableau de bord d'une opération spécifique
    """
    id = serializers.IntegerField()
    nom = serializers.CharField()
    progression = serializers.FloatField()
    
    # Statut couleur
    statut_cout = serializers.CharField()
    statut_delai = serializers.CharField()
    statut_global = serializers.CharField()
    
    # Coût
    cout_prevue = serializers.DecimalField(max_digits=15, decimal_places=2)
    cout_reel = serializers.DecimalField(max_digits=15, decimal_places=2)
    ecart_cout = serializers.DecimalField(max_digits=15, decimal_places=2)
    pourcentage_ecart_cout = serializers.FloatField()
    
    # Délais
    date_debut_prevue = serializers.DateField()
    date_fin_prevue = serializers.DateField()
    date_debut_reelle = serializers.DateField(allow_null=True)
    date_fin_reelle = serializers.DateField(allow_null=True)
    retard_jours = serializers.IntegerField()
    
    # Problèmes
    problemes_ouverts = serializers.IntegerField()
    problemes_en_cours = serializers.IntegerField()
    problemes_resolus = serializers.IntegerField()


class IndicateursPerformanceSerializer(serializers.Serializer):
    """
    Sérialiseur pour les indicateurs de performance
    """
    efficacite = serializers.FloatField()
    productivite_cout = serializers.DecimalField(max_digits=15, decimal_places=2)
    productivite_temps = serializers.FloatField()
    qualite_problemes = serializers.FloatField()
    temps_resolution_moyen = serializers.FloatField()


class IndicateursEquipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom_complet = serializers.CharField()
    role_projet = serializers.CharField()
    operations_assignees = serializers.IntegerField()
    progression_moyenne = serializers.FloatField()

    def to_representation(self, instance):
        if isinstance(instance, dict):
            # Handle dictionary input
            return {
                'id': instance.get('id') or instance.get('utilisateur', {}).get('id'),
                'nom_complet': instance.get('nom_complet', '') or 
                              f"{instance.get('utilisateur', {}).get('prenom', '')} {instance.get('utilisateur', {}).get('nom', '')}",
                'role_projet': instance.get('role_projet', ''),
                'operations_assignees': instance.get('operations_assignees', 0),
                'progression_moyenne': instance.get('progression_moyenne', 0.0),
            }
        
        # Handle model instance (EquipeProjet)
        operations = Operation.objects.filter(
            responsable=instance.utilisateur,
            phase__projet=instance.projet
        )
        
        progression_moyenne = 0.0
        if operations.exists():
            total = sum(op.progression for op in operations)
            progression_moyenne = round(total / operations.count(), 2)

        return {
            'id': instance.utilisateur.id,
            'nom_complet': instance.utilisateur.get_full_name(),
            'role_projet': instance.role_projet,
            'operations_assignees': operations.count(),
            'progression_moyenne': progression_moyenne,
        }

class StatistiquesEquipeProjetSerializer(serializers.Serializer):
    """
    Sérialiseur pour les statistiques globales de l'équipe du projet
    """
    nombre_membres = serializers.IntegerField()
    ingenieur_terrain = serializers.IntegerField()
    expert = serializers.IntegerField()
    top_management = serializers.IntegerField()