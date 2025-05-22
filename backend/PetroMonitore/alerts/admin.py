from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from ..models import Alerte


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'type_alerte', 'niveau_badge', 'statut_badge', 
        'projet_link', 'message_court', 'date_alerte', 'lue_par'
    ]
    
    list_filter = [
        'niveau', 'statut', 'type_alerte', 'date_alerte',
        ('projet', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'type_alerte', 'message', 'projet__nom', 
        'phase__nom', 'operation__nom'
    ]
    
    readonly_fields = ['date_alerte', 'date_lecture']
    
    fieldsets = (
        ('Information Générale', {
            'fields': ('type_alerte', 'niveau', 'message', 'statut')
        }),
        ('Contexte', {
            'fields': ('projet', 'phase', 'operation'),
            'classes': ('collapse',)
        }),
        ('Suivi', {
            'fields': ('date_alerte', 'lue_par', 'date_lecture'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marquer_comme_lues', 'marquer_comme_traitees', 'supprimer_alertes_anciennes']
    
    def niveau_badge(self, obj):
        """Affichage coloré du niveau"""
        couleurs = {
            'INFO': '#17a2b8',
            'WARNING': '#ffc107', 
            'CRITIQUE': '#dc3545'
        }
        couleur = couleurs.get(obj.niveau, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            couleur, obj.get_niveau_display()
        )
    niveau_badge.short_description = 'Niveau'
    niveau_badge.admin_order_field = 'niveau'
    
    def statut_badge(self, obj):
        """Affichage coloré du statut"""
        couleurs = {
            'NON_LU': '#dc3545',    # Rouge
            'LU': '#ffc107',        # Jaune
            'TRAITEE': '#28a745'    # Vert
        }
        couleur = couleurs.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            couleur, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    statut_badge.admin_order_field = 'statut'
    
    def projet_link(self, obj):
        """Lien vers le projet"""
        if obj.projet:
            url = reverse('admin:PteroMonitore_projet_change', args=[obj.projet.pk])
            return format_html('<a href="{}">{}</a>', url, obj.projet.nom)
        return '-'
    projet_link.short_description = 'Projet'
    projet_link.admin_order_field = 'projet__nom'
    
    def message_court(self, obj):
        """Message tronqué"""
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_court.short_description = 'Message'
    
    def marquer_comme_lues(self, request, queryset):
        """Action pour marquer les alertes comme lues"""
        count = queryset.filter(statut='NON_LU').update(
            statut='LU',
            lue_par=request.user,
            date_lecture=timezone.now()
        )
        self.message_user(request, f'{count} alertes marquées comme lues.')
    marquer_comme_lues.short_description = 'Marquer comme lues'
    
    def marquer_comme_traitees(self, request, queryset):
        """Action pour marquer les alertes comme traitées"""
        from django.utils import timezone
        count = queryset.filter(statut__in=['NON_LU', 'LU']).update(
            statut='TRAITEE',
            lue_par=request.user,
            date_lecture=timezone.now()
        )
        self.message_user(request, f'{count} alertes marquées comme traitées.')
    marquer_comme_traitees.short_description = 'Marquer comme traitées'
    
    def supprimer_alertes_anciennes(self, request, queryset):
        """Action pour supprimer les anciennes alertes traitées"""
        from datetime import timedelta
        from django.utils import timezone
        
        date_limite = timezone.now() - timedelta(days=30)
        count = queryset.filter(
            statut='TRAITEE',
            date_alerte__lt=date_limite
        ).delete()[0]
        
        self.message_user(request, f'{count} anciennes alertes supprimées.')
    supprimer_alertes_anciennes.short_description = 'Supprimer alertes anciennes (>30j)'