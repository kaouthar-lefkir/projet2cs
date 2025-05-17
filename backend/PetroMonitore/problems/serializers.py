from rest_framework import serializers
from ..models import Probleme, Solution, Utilisateur, Projet, Phase, Operation, Rapport
from datetime import datetime

class UtilisateurMinSerializer(serializers.ModelSerializer):
    """Serializer pour les informations minimales d'un utilisateur."""
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'prenom', 'email', 'role', 'nom_complet']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"


class ProblemeListSerializer(serializers.ModelSerializer):
    """Serializer pour liste des problèmes"""
    signale_par_nom = serializers.SerializerMethodField()
    resolu_par_nom = serializers.SerializerMethodField()
    projet_nom = serializers.SerializerMethodField()
    phase_nom = serializers.SerializerMethodField()
    operation_nom = serializers.SerializerMethodField()
    nb_solutions = serializers.SerializerMethodField()
    
    class Meta:
        model = Probleme
        fields = ['id', 'titre', 'description', 'gravite', 'statut', 
                  'date_signalement', 'signale_par', 'signale_par_nom',
                  'date_resolution', 'resolu_par', 'resolu_par_nom',
                  'projet', 'projet_nom', 'phase', 'phase_nom', 
                  'operation', 'operation_nom', 'rapport', 'nb_solutions']
    
    def get_signale_par_nom(self, obj):
        if obj.signale_par:
            return f"{obj.signale_par.prenom} {obj.signale_par.nom}"
        return None
    
    def get_resolu_par_nom(self, obj):
        if obj.resolu_par:
            return f"{obj.resolu_par.prenom} {obj.resolu_par.nom}"
        return None
    
    def get_projet_nom(self, obj):
        if obj.projet:
            return obj.projet.nom
        return None
    
    def get_phase_nom(self, obj):
        if obj.phase:
            return obj.phase.nom
        return None
    
    def get_operation_nom(self, obj):
        if obj.operation:
            return obj.operation.nom
        return None
    
    def get_nb_solutions(self, obj):
        return obj.solutions.count()


class ProblemeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création d'un problème"""
    class Meta:
        model = Probleme
        fields = ['titre', 'description', 'gravite', 'statut', 
                  'projet', 'phase', 'operation', 'rapport']
    
    def validate(self, data):
        # Vérifier la cohérence projet/phase/operation
        projet = data.get('projet')
        phase = data.get('phase')
        operation = data.get('operation')
        
        # Si phase spécifiée, vérifier qu'elle appartient au projet
        if phase and projet and phase.projet.id != projet.id:
            raise serializers.ValidationError({
                "phase": "La phase sélectionnée n'appartient pas au projet indiqué"
            })
        
        # Si opération spécifiée, vérifier qu'elle appartient à la phase
        if operation and phase and operation.phase.id != phase.id:
            raise serializers.ValidationError({
                "operation": "L'opération sélectionnée n'appartient pas à la phase indiquée"
            })
        
        # Si opération spécifiée sans phase, vérifier cohérence avec projet
        if operation and not phase and projet and operation.phase.projet.id != projet.id:
            raise serializers.ValidationError({
                "operation": "L'opération sélectionnée n'appartient pas au projet indiqué"
            })
            
        return data

    def create(self, validated_data):
        # Récupérer l'utilisateur qui crée le problème
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['signale_par'] = request.user
        
        return super().create(validated_data)


class ProblemeUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour modification d'un problème"""
    class Meta:
        model = Probleme
        fields = ['titre', 'description', 'gravite', 'statut']
    
    def update(self, instance, validated_data):
        # Si le statut passe à "RESOLU", mettre à jour date_resolution et resolu_par
        if validated_data.get('statut') == 'RESOLU' and instance.statut != 'RESOLU':
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['resolu_par'] = request.user
            validated_data['date_resolution'] = datetime.now()
        
        return super().update(instance, validated_data)


class SolutionListSerializer(serializers.ModelSerializer):
    """Serializer pour liste des solutions"""
    proposee_par_nom = serializers.SerializerMethodField()
    validee_par_nom = serializers.SerializerMethodField()
    probleme_titre = serializers.SerializerMethodField()
    
    class Meta:
        model = Solution
        fields = ['id', 'description', 'type_solution', 'cout_estime', 
                  'delai_estime', 'proposee_par', 'proposee_par_nom',
                  'date_proposition', 'statut', 'date_validation', 
                  'validee_par', 'validee_par_nom', 'probleme', 'probleme_titre']
    
    def get_proposee_par_nom(self, obj):
        if obj.proposee_par:
            return f"{obj.proposee_par.prenom} {obj.proposee_par.nom}"
        return None
    
    def get_validee_par_nom(self, obj):
        if obj.validee_par:
            return f"{obj.validee_par.prenom} {obj.validee_par.nom}"
        return None
    
    def get_probleme_titre(self, obj):
        return obj.probleme.titre if obj.probleme else None


class SolutionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création d'une solution"""
    class Meta:
        model = Solution
        fields = ['probleme', 'description', 'type_solution', 'cout_estime', 'delai_estime']
    
    def create(self, validated_data):
        # Récupérer l'utilisateur qui propose la solution
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['proposee_par'] = request.user
        
        return super().create(validated_data)


class SolutionUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour modification d'une solution"""
    class Meta:
        model = Solution
        fields = ['description', 'type_solution', 'cout_estime', 'delai_estime', 'statut']
    
    def update(self, instance, validated_data):
        # Si le statut passe à "VALIDEE", mettre à jour date_validation et validee_par
        if validated_data.get('statut') == 'VALIDEE' and instance.statut != 'VALIDEE':
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['validee_par'] = request.user
            validated_data['date_validation'] = datetime.now()
        
        return super().update(instance, validated_data)


class ProblemeDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un problème avec ses solutions"""
    solutions = SolutionListSerializer(many=True, read_only=True)
    signale_par = UtilisateurMinSerializer(read_only=True)
    resolu_par = UtilisateurMinSerializer(read_only=True)
    projet_nom = serializers.SerializerMethodField()
    phase_nom = serializers.SerializerMethodField()
    operation_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Probleme
        fields = ['id', 'titre', 'description', 'gravite', 'statut', 
                  'date_signalement', 'signale_par', 'date_resolution', 
                  'resolu_par', 'projet', 'projet_nom', 'phase', 'phase_nom', 
                  'operation', 'operation_nom', 'rapport', 'solutions']
    
    def get_projet_nom(self, obj):
        if obj.projet:
            return obj.projet.nom
        return None
    
    def get_phase_nom(self, obj):
        if obj.phase:
            return obj.phase.nom
        return None
    
    def get_operation_nom(self, obj):
        if obj.operation:
            return obj.operation.nom
        return None