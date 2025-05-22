# PteroMonitore/alerts/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .utils import detecter_toutes_alertes, nettoyer_anciennes_alertes, generer_rapport_alertes
from ..models import Alerte

logger = logging.getLogger(__name__)


@shared_task
def detecter_alertes_periodique():
    """
    Tâche périodique pour détecter les alertes automatiquement
    """
    try:
        logger.info("Début de la détection périodique des alertes")
        alertes_creees = detecter_toutes_alertes()
        logger.info(f"Détection terminée: {len(alertes_creees)} nouvelles alertes créées")
        return f"Détection terminée: {len(alertes_creees)} alertes créées"
        
    except Exception as e:
        logger.error(f"Erreur lors de la détection périodique: {str(e)}")
        return f"Erreur: {str(e)}"


@shared_task
def nettoyer_alertes_periodique():
    """
    Tâche périodique pour nettoyer les anciennes alertes
    """
    try:
        logger.info("Début du nettoyage des anciennes alertes")
        count = nettoyer_anciennes_alertes(jours=60)  # Supprimer après 60 jours
        logger.info(f"Nettoyage terminé: {count} alertes supprimées")
        return f"Nettoyage terminé: {count} alertes supprimées"
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage périodique: {str(e)}")
        return f"Erreur: {str(e)}"


@shared_task
def generer_rapport_hebdomadaire():
    """
    Générer un rapport hebdomadaire des alertes
    """
    try:
        logger.info("Génération du rapport hebdomadaire des alertes")
        
        date_fin = timezone.now()
        date_debut = date_fin - timedelta(days=7)
        
        rapport = generer_rapport_alertes(date_debut, date_fin)
        
        if rapport:
            # Ici vous pouvez envoyer le rapport par email aux responsables
            # ou l'enregistrer dans la base de données
            logger.info("Rapport hebdomadaire généré avec succès")
            return "Rapport hebdomadaire généré"
        else:
            logger.error("Échec de la génération du rapport")
            return "Erreur lors de la génération du rapport"
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        return f"Erreur: {str(e)}"


@shared_task
def envoyer_resume_alertes_quotidien():
    """
    Envoyer un résumé quotidien des alertes aux responsables
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from ..models import Utilisateur
        
        logger.info("Envoi du résumé quotidien des alertes")
        
        # Alertes du jour
        aujourd_hui = timezone.now().date()
        alertes_jour = Alerte.objects.filter(
            date_alerte__date=aujourd_hui
        ).select_related('projet', 'phase', 'operation')
        
        # Alertes non traitées
        alertes_non_traitees = Alerte.objects.filter(
            statut__in=['NON_LU', 'LU']
        ).count()
        
        # Alertes critiques non traitées
        alertes_critiques = Alerte.objects.filter(
            niveau='CRITIQUE',
            statut__in=['NON_LU', 'LU']
        ).count()
        
        if alertes_jour.exists() or alertes_non_traitees > 0:
            # Construire le message
            message = f"""
RÉSUMÉ QUOTIDIEN DES ALERTES - {aujourd_hui.strftime('%d/%m/%Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATISTIQUES
• Nouvelles alertes aujourd'hui: {alertes_jour.count()}
• Alertes non traitées: {alertes_non_traitees}
• Alertes critiques non traitées: {alertes_critiques}

"""
            
            if alertes_jour.exists():
                message += "\n🚨 NOUVELLES ALERTES AUJOURD'HUI:\n"
                for alerte in alertes_jour:
                    projet_nom = alerte.projet.nom if alerte.projet else "N/A"
                    message += f"• [{alerte.niveau}] {alerte.type_alerte} - {projet_nom}\n"
                    message += f"  {alerte.message}\n\n"
            
            if alertes_critiques > 0:
                message += f"\n⚠️  ATTENTION: {alertes_critiques} alertes critiques nécessitent une intervention immédiate!\n"
            
            message += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Connectez-vous au système de monitoring pour traiter ces alertes.
"""
            
            # Envoyer aux responsables
            destinataires = list(Utilisateur.objects.filter(
                role__in=['EXPERT', 'TOP_MANAGEMENT'],
                statut='ACTIF'
            ).values_list('email', flat=True))
            
            if destinataires:
                send_mail(
                    subject=f"📊 Résumé quotidien des alertes - {aujourd_hui.strftime('%d/%m/%Y')}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=destinataires,
                    fail_silently=True
                )
                
                logger.info(f"Résumé quotidien envoyé à {len(destinataires)} destinataires")
                return f"Résumé envoyé à {len(destinataires)} destinataires"
            else:
                logger.warning("Aucun destinataire trouvé pour le résumé quotidien")
                return "Aucun destinataire trouvé"
        else:
            logger.info("Aucune alerte à signaler aujourd'hui")
            return "Aucune alerte à signaler"
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du résumé quotidien: {str(e)}")
        return f"Erreur: {str(e)}"


@shared_task
def verifier_alertes_projet(projet_id):
    """
    Vérifier les alertes pour un projet spécifique
    """
    try:
        from ..models import Projet
        from .utils import verifier_seuils_projet, verifier_progression_anormale
        
        projet = Projet.objects.get(id=projet_id)
        alertes_creees = []
        
        # Vérifier les seuils
        alertes_creees.extend(verifier_seuils_projet(projet))
        
        # Vérifier la progression
        alertes_creees.extend(verifier_progression_anormale(projet))
        
        logger.info(f"Vérification projet {projet.nom}: {len(alertes_creees)} alertes créées")
        return f"{len(alertes_creees)} alertes créées pour le projet {projet.nom}"
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du projet {projet_id}: {str(e)}")
        return f"Erreur: {str(e)}"