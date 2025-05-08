from django.contrib import admin
from .models import Utilisateur, Projet, Phase, Operation, Seuil, Rapport, Probleme, Solution, EquipeProjet, Alerte, HistoriqueModification

# Configuration de l'interface d'administration pour le modèle Utilisateur
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'role', 'statut', 'date_creation')
    list_filter = ('role', 'statut')
    search_fields = ('nom', 'prenom', 'email')
    ordering = ('nom', 'prenom')
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'mot_de_passe')
        }),
        ('Paramètres du compte', {
            'fields': ('role', 'statut')
        }),
    )
    readonly_fields = ('date_creation',)

# Enregistrement des autres modèles avec des configurations par défaut
admin.site.register(Projet)
admin.site.register(Phase)
admin.site.register(Operation)
admin.site.register(Seuil)
admin.site.register(Rapport)
admin.site.register(Probleme)
admin.site.register(Solution)
admin.site.register(EquipeProjet)
admin.site.register(Alerte)
admin.site.register(HistoriqueModification)