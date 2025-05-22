# PteroMonitore/alerts/serializers.py
from rest_framework import serializers
from ..models import Alerte, Projet, Phase, Operation, Utilisateur


class UtilisateurSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour l'utilisateur
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'prenom', 'email', 'full_name']


class ProjetSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour le projet
    """
    class Meta:
        model = Projet
        fields = ['id', 'nom', 'statut', 'localisation']


class PhaseSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour la phase
    """
    class Meta:
        model = Phase
        fields = ['id', 'nom', 'statut', 'ordre']


class OperationSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour l'opération
    """
    class Meta:
        model = Operation
        fields = ['id', 'nom', 'statut', 'type_operation']


class AlerteSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour les alertes
    """
    projet = ProjetSimpleSerializer(read_only=True)
    phase = PhaseSimpleSerializer(read_only=True)
    operation = OperationSimpleSerializer(read_only=True)
    lue_par = UtilisateurSimpleSerializer(read_only=True)
    
    # Champs calculés
    temps_ecoule = serializers.SerializerMethodField()
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Alerte
        fields = [
            'id', 'projet', 'phase', 'operation', 'type_alerte',
            'niveau', 'niveau_display', 'message', 'date_alerte',
            'statut', 'statut_display', 'lue_par', 'date_lecture',
            'temps_ecoule'
        ]
    
    def get_temps_ecoule(self, obj):
        """
        Calcule le temps écoulé depuis la création de l'alerte
        """
        from django.utils import timezone
        delta = timezone.now() - obj.date_alerte
        
        if delta.days > 0:
            return f"{delta.days} jour{'s' if delta.days > 1 else ''}"
        elif delta.seconds > 3600:
            heures = delta.seconds // 3600
            return f"{heures} heure{'s' if heures > 1 else ''}"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "À l'instant"


class AlerteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'alertes
    """
    class Meta:
        model = Alerte
        fields = [
            'projet', 'phase', 'operation', 'type_alerte',
            'niveau', 'message'
        ]
    
    def validate(self, data):
        """
        Validation des données
        """
        # Au moins un élément (projet, phase, ou opération) doit être spécifié
        if not any([data.get('projet'), data.get('phase'), data.get('operation')]):
            raise serializers.ValidationError(
                "Au moins un élément (projet, phase, ou opération) doit être spécifié."
            )
        
        # Vérifier la cohérence des relations
        if data.get('phase') and data.get('projet'):
            if data['phase'].projet != data['projet']:
                raise serializers.ValidationError(
                    "La phase spécifiée n'appartient pas au projet spécifié."
                )
        
        if data.get('operation') and data.get('phase'):
            if data['operation'].phase != data['phase']:
                raise serializers.ValidationError(
                    "L'opération spécifiée n'appartient pas à la phase spécifiée."
                )
        
        return data


class AlerteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour d'alertes
    """
    class Meta:
        model = Alerte
        fields = ['statut', 'message']
        
    def validate_statut(self, value):
        """
        Validation du statut
        """
        if value not in ['NON_LU', 'LU', 'TRAITEE']:
            raise serializers.ValidationError("Statut invalide.")
        return value


class AlerteHistoriqueSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des alertes
    """
    projet_nom = serializers.CharField(source='projet.nom', read_only=True)
    phase_nom = serializers.CharField(source='phase.nom', read_only=True)
    operation_nom = serializers.CharField(source='operation.nom', read_only=True)
    lue_par_nom = serializers.CharField(source='lue_par.get_full_name', read_only=True)
    
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Alerte
        fields = [
            'id', 'type_alerte', 'niveau', 'niveau_display',
            'message', 'date_alerte', 'statut', 'statut_display',
            'date_lecture', 'projet_nom', 'phase_nom', 'operation_nom',
            'lue_par_nom'
        ]


class AlerteStatistiquesSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques d'alertes
    """
    total_alertes = serializers.IntegerField()
    alertes_non_lues = serializers.IntegerField()
    alertes_critiques = serializers.IntegerField()
    alertes_recentes = serializers.IntegerField()
    par_niveau = serializers.ListField()
    par_statut = serializers.ListField()
    par_type = serializers.ListField()


class AlerteTableauBordSerializer(serializers.ModelSerializer):
    """
    Serializer pour les alertes du tableau de bord
    """
    projet_nom = serializers.CharField(source='projet.nom', read_only=True)
    temps_ecoule = serializers.SerializerMethodField()
    niveau_couleur = serializers.SerializerMethodField()
    
    class Meta:
        model = Alerte
        fields = [
            'id', 'type_alerte', 'niveau', 'message',
            'date_alerte', 'statut', 'projet_nom',
            'temps_ecoule', 'niveau_couleur'
        ]
    
    def get_temps_ecoule(self, obj):
        """
        Temps écoulé depuis la création
        """
        from django.utils import timezone
        delta = timezone.now() - obj.date_alerte
        
        if delta.days > 0:
            return f"{delta.days}j"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h"
        else:
            return f"{delta.seconds // 60}m"
    
    def get_niveau_couleur(self, obj):
        """
        Couleur associée au niveau d'alerte
        """
        couleurs = {
            'INFO': '#17a2b8',      # Bleu
            'WARNING': '#ffc107',   # Jaune
            'CRITIQUE': '#dc3545'   # Rouge
        }
        return couleurs.get(obj.niveau, '#6c757d')