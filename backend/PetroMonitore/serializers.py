from rest_framework import serializers
from .models import HistoriqueModification, Projet, Phase, Operation, Utilisateur, EquipeProjet
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'nom', 'prenom', 'role', 'statut', 'date_creation']
        read_only_fields = ['id', 'date_creation']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['email', 'nom', 'prenom', 'mot_de_passe', 'role', 'statut']
        extra_kwargs = {'mot_de_passe': {'write_only': True}}

    def create(self, validated_data):
        validated_data['mot_de_passe'] = make_password(validated_data['mot_de_passe'])
        return super().create(validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['email', 'nom', 'prenom', 'role', 'statut']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    mot_de_passe = serializers.CharField()
    
    
# Serializers pour les projets
class ProjetSerializer(serializers.ModelSerializer):
    responsable_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Projet
        fields = ['id', 'nom', 'description', 'localisation', 'budget_initial', 
                 'cout_actuel', 'date_debut', 'date_fin_prevue', 'date_fin_reelle', 
                 'statut', 'responsable', 'responsable_nom', 'date_creation']
    
    def get_responsable_nom(self, obj):
        if obj.responsable:
            return f"{obj.responsable.prenom} {obj.responsable.nom}"
        return None


class ProjetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'localisation', 'budget_initial', 
                 'date_debut', 'date_fin_prevue', 'statut', 'responsable',
                 'seuil_alerte_cout', 'seuil_alerte_delai']
    
    def validate(self, data):
        # Vérification que la date de fin est après la date de début
        if 'date_debut' in data and 'date_fin_prevue' in data and data['date_debut'] and data['date_fin_prevue']:
            if data['date_fin_prevue'] < data['date_debut']:
                raise serializers.ValidationError({"date_fin_prevue": "La date de fin doit être postérieure à la date de début"})
        
        # Vérification que le budget initial est positif
        if 'budget_initial' in data and data['budget_initial'] and data['budget_initial'] < 0:
            raise serializers.ValidationError({"budget_initial": "Le budget initial doit être positif"})
        
        return data


class ProjetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'localisation', 'budget_initial', 
                 'date_debut', 'date_fin_prevue', 'date_fin_reelle', 
                 'statut', 'responsable', 'seuil_alerte_cout', 'seuil_alerte_delai']
    
    def validate(self, data):
        # Vérification que la date de fin est après la date de début
        if 'date_debut' in data and 'date_fin_prevue' in data and data['date_debut'] and data['date_fin_prevue']:
            if data['date_fin_prevue'] < data['date_debut']:
                raise serializers.ValidationError({"date_fin_prevue": "La date de fin doit être postérieure à la date de début"})
        
        # Vérification que le budget initial est positif
        if 'budget_initial' in data and data['budget_initial'] and data['budget_initial'] < 0:
            raise serializers.ValidationError({"budget_initial": "Le budget initial doit être positif"})
        
        return data


class PhaseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ['id', 'nom', 'ordre', 'date_debut_prevue', 'date_fin_prevue', 
                  'date_debut_reelle', 'date_fin_reelle', 'budget_alloue', 
                  'cout_actuel', 'progression', 'statut']


class EquipeProjetSerializer(serializers.ModelSerializer):
    utilisateur_details = UserSerializer(source='utilisateur', read_only=True)
    
    class Meta:
        model = EquipeProjet
        fields = ['id', 'utilisateur', 'utilisateur_details', 'role_projet', 'date_affectation']


class ProjetDetailSerializer(serializers.ModelSerializer):
    phases = PhaseSimpleSerializer(many=True, read_only=True)
    responsable_details = UserSerializer(source='responsable', read_only=True)
    membres_equipe = EquipeProjetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Projet
        fields = ['id', 'nom', 'description', 'localisation', 'budget_initial', 
                 'cout_actuel', 'date_debut', 'date_fin_prevue', 'date_fin_reelle', 
                 'statut', 'responsable', 'responsable_details', 'seuil_alerte_cout', 
                 'seuil_alerte_delai', 'date_creation', 'phases', 'membres_equipe']
        
        
class OperationSerializer(serializers.ModelSerializer):
    """
    Serializer for Operation model
    """
    class Meta:
        model = Operation
        fields = '__all__'
        read_only_fields = ['id', 'date_creation']

class OperationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Operation
    """
    class Meta:
        model = Operation
        exclude = ['id']
        extra_kwargs = {
            'phase': {'required': True}
        }

class OperationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Operation
    """
    class Meta:
        model = Operation
        exclude = ['id', 'phase']

class PhaseSerializer(serializers.ModelSerializer):
    """
    Serializer for Phase model with operations
    """
    operations = OperationSerializer(many=True, read_only=True)

    class Meta:
        model = Phase
        fields = '__all__'
        read_only_fields = ['id', 'date_creation']

class PhaseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Phase
    """
    class Meta:
        model = Phase
        exclude = ['id']
        extra_kwargs = {
            'projet': {'required': True}
        }

class PhaseUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Phase
    """
    class Meta:
        model = Phase
        exclude = ['id', 'projet']
        
        

class UtilisateurMinSerializer(serializers.ModelSerializer):
    """Serializer pour les informations minimales d'un utilisateur."""
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'prenom', 'email', 'role', 'nom_complet']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"


class ProjetMinSerializer(serializers.ModelSerializer):
    """Serializer pour les informations minimales d'un projet."""
    class Meta:
        model = Projet
        fields = ['id', 'nom', 'statut']


class EquipeProjetSerializer(serializers.ModelSerializer):
    """Serializer pour les opérations de base sur EquipeProjet."""
    class Meta:
        model = EquipeProjet
        fields = ['id', 'projet', 'utilisateur', 'role_projet', 'date_affectation', 'affecte_par']
        read_only_fields = ['date_affectation', 'affecte_par']
    
    def update(self, instance, validated_data):
        old_values = {
            'role_projet': instance.role_projet,
        }
    
        instance = super().update(instance, validated_data)
    
        request = self.context.get('request')
        user = request.user if request else None
    
        for field, old_value in old_values.items():
            if field in validated_data and validated_data[field] != old_value:
                HistoriqueModification.objects.create(
                    table_modifiee='EquipeProjet',
                    id_enregistrement=instance.id,  # This is the missing field
                    champ_modifie=field,
                    ancienne_valeur=old_value,
                    nouvelle_valeur=validated_data[field],
                    modifie_par=user
                )
                
        return instance


class EquipeProjetDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour EquipeProjet avec les données utilisateur et projet."""
    utilisateur = UtilisateurMinSerializer(read_only=True)
    projet = ProjetMinSerializer(read_only=True)
    affecte_par = UtilisateurMinSerializer(read_only=True)
    
    class Meta:
        model = EquipeProjet
        fields = ['id', 'projet', 'utilisateur', 'role_projet', 'date_affectation', 'affecte_par']