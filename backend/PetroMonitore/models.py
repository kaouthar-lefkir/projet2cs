from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('INGENIEUR_TERRAIN', 'Ingénieur Terrain'),
        ('EXPERT', 'Expert'),
        ('TOP_MANAGEMENT', 'Top Management'),
    )
    STATUT_CHOICES = (
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('SUSPENDU', 'Suspendu'),
    )
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UtilisateurManager()

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def get_short_name(self):
        return self.prenom

    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.mot_de_passe)

    @property
    def password(self):
        return self.mot_de_passe

    @password.setter
    def password(self, raw_password):
        self.set_password(raw_password)

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    

class Projet(models.Model):
    STATUT_CHOICES = (
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('SUSPENDU', 'Suspendu'),
    )
    
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    localisation = models.CharField(max_length=200, blank=True, null=True)
    budget_initial = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cout_actuel = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='projets_responsable')
    seuil_alerte_cout = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    seuil_alerte_delai = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom


class Phase(models.Model):
    STATUT_CHOICES = (
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('SUSPENDU', 'Suspendu'),
    )
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='phases')
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ordre = models.IntegerField()
    date_debut_prevue = models.DateField(blank=True, null=True)
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_debut_reelle = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)
    budget_alloue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cout_actuel = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    progression = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    
    def __str__(self):
        return f"{self.projet.nom} - {self.nom}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update phase progress after saving
        and to handle skip_update flag to avoid recursion
        """
        # Check if we should skip the update_phase_progress call
        skip_update = kwargs.pop('skip_update', False)
        
        # Call the "real" save method
        super().save(*args, **kwargs)
        
        # Only update phase progress if not explicitly skipped
        if not skip_update:
            from .utils import update_phase_progress
            update_phase_progress(self.id)
    
    class Meta:
        ordering = ['ordre']


class Operation(models.Model):
    STATUT_CHOICES = (
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('SUSPENDU', 'Suspendu'),
    )
    
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='operations')
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    type_operation = models.CharField(max_length=100, blank=True, null=True)
    date_debut_prevue = models.DateField(blank=True, null=True)
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_debut_reelle = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)
    cout_prevue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cout_reel = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    progression = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES)
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='operations_responsable')
    
    def __str__(self):
        return f"{self.phase.nom} - {self.nom}"


class Seuil(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='seuils')
    valeur_verte = models.DecimalField(max_digits=10, decimal_places=2)
    valeur_jaune = models.DecimalField(max_digits=10, decimal_places=2)
    valeur_rouge = models.DecimalField(max_digits=10, decimal_places=2)
    date_definition = models.DateTimeField(auto_now_add=True)
    defini_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='seuils_definis')
    date_modification = models.DateTimeField(blank=True, null=True)
    modifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='seuils_modifies')
    
    def __str__(self):
        return f"{self.operation.nom} - {self.type_seuil}"


class Rapport(models.Model):
    STATUT_CHOICES = (
        ('A_TRAITER', 'À traiter'),
        ('TRAITE', 'Traité'),
        ('REJETE', 'Rejeté'),
    )
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='rapports', blank=True, null=True)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='rapports', blank=True, null=True)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='rapports', blank=True, null=True)
    type_rapport = models.CharField(max_length=100)
    nom_fichier = models.CharField(max_length=255, blank=True, null=True)
    chemin_fichier = models.CharField(max_length=500, blank=True, null=True)
    date_import = models.DateTimeField(auto_now_add=True)
    importe_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='rapports_importes')
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='A_TRAITER')
    commentaires = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.type_rapport} - {self.nom_fichier}"


class Probleme(models.Model):
    GRAVITE_CHOICES = (
        ('FAIBLE', 'Faible'),
        ('MOYENNE', 'Moyenne'),
        ('ELEVEE', 'Élevée'),
        ('CRITIQUE', 'Critique'),
    )
    STATUT_CHOICES = (
        ('OUVERT', 'Ouvert'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('FERME', 'Fermé'),
    )
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='problemes', blank=True, null=True)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='problemes', blank=True, null=True)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='problemes', blank=True, null=True)
    rapport = models.ForeignKey(Rapport, on_delete=models.SET_NULL, related_name='problemes', blank=True, null=True)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    gravite = models.CharField(max_length=50, choices=GRAVITE_CHOICES)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='OUVERT')
    date_signalement = models.DateTimeField(auto_now_add=True)
    signale_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='problemes_signales')
    date_resolution = models.DateTimeField(blank=True, null=True)
    resolu_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='problemes_resolus')
    
    def __str__(self):
        return self.titre


class Solution(models.Model):
    STATUT_CHOICES = (
        ('PROPOSEE', 'Proposée'),
        ('VALIDEE', 'Validée'),
        ('REJETEE', 'Rejetée'),
        ('MISE_EN_OEUVRE', 'Mise en œuvre'),
    )
    
    probleme = models.ForeignKey(Probleme, on_delete=models.CASCADE, related_name='solutions')
    description = models.TextField()
    type_solution = models.CharField(max_length=100, blank=True, null=True)
    cout_estime = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    delai_estime = models.IntegerField(blank=True, null=True)
    proposee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='solutions_proposees')
    date_proposition = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='PROPOSEE')
    date_validation = models.DateTimeField(blank=True, null=True)
    validee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='solutions_validees')
    
    def __str__(self):
        return f"Solution for {self.probleme.titre}"


class EquipeProjet(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='membres_equipe')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='equipes')
    role_projet = models.CharField(max_length=100)
    date_affectation = models.DateTimeField(auto_now_add=True)
    affecte_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='affectations')
    
    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom} - {self.projet.nom}"
    
    class Meta:
        unique_together = ('projet', 'utilisateur')


class Alerte(models.Model):
    NIVEAU_CHOICES = (
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('CRITIQUE', 'Critique'),
    )
    STATUT_CHOICES = (
        ('NON_LU', 'Non lu'),
        ('LU', 'Lu'),
        ('TRAITEE', 'Traitée'),
    )
    
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='alertes', blank=True, null=True)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='alertes', blank=True, null=True)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='alertes', blank=True, null=True)
    type_alerte = models.CharField(max_length=100)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    message = models.CharField(max_length=500)
    date_alerte = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='NON_LU')
    lue_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='alertes_lues')
    date_lecture = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.type_alerte} - {self.projet.nom if self.projet else 'N/A'}"


class HistoriqueModification(models.Model):
    table_modifiee = models.CharField(max_length=100)
    id_enregistrement = models.IntegerField()
    champ_modifie = models.CharField(max_length=100)
    ancienne_valeur = models.TextField(blank=True, null=True)
    nouvelle_valeur = models.TextField(blank=True, null=True)
    date_modification = models.DateTimeField(auto_now_add=True)
    modifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, blank=True, null=True, related_name='modifications')
    commentaire = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.table_modifiee} - {self.id_enregistrement} - {self.champ_modifie}"
