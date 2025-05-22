# PteroMonitore/alerts/utils.py
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from datetime import timedelta
import logging

from ..models import Alerte, Projet, Phase, Operation, Seuil

logger = logging.getLogger(__name__)


def creer_alerte(type_alerte, niveau, message, projet=None, phase=None, operation=None):
    """
    Créer une nouvelle alerte
    """
    try:
        alerte = Alerte.objects.create(
            projet=projet,
            phase=phase,
            operation=operation,
            type_alerte=type_alerte,
            niveau=niveau,
            message=message
        )
        
        # Envoyer notification
        envoyer_notification_alerte(alerte)
        
        return alerte
        
    except Exception as e:
        logger.error(f"Erreur lors de la création d'alerte: {str(e)}")
        return None


def verifier_seuils_projet(projet):
    """
    Vérifier les seuils d'un projet et créer des alertes si nécessaire
    """
    alertes_creees = []
    
    try:
        # Vérification budget
        if (projet.budget_initial and projet.cout_actuel and 
            projet.seuil_alerte_cout):
            
            pourcentage_utilise = (projet.cout_actuel / projet.budget_initial) * 100
            
            if pourcentage_utilise >= projet.seuil_alerte_cout:
                # Vérifier si une alerte similaire n'existe pas déjà
                alerte_existante = Alerte.objects.filter(
                    projet=projet,
                    type_alerte='DEPASSEMENT_BUDGET',
                    statut__in=['NON_LU', 'LU']
                ).exists()
                
                if not alerte_existante:
                    niveau = 'CRITIQUE' if pourcentage_utilise >= 100 else 'WARNING'
                    message = f"Budget utilisé à {pourcentage_utilise:.1f}% ({projet.cout_actuel}€ / {projet.budget_initial}€)"
                    
                    alerte = creer_alerte(
                        'DEPASSEMENT_BUDGET',
                        niveau,
                        message,
                        projet=projet
                    )
                    
                    if alerte:
                        alertes_creees.append(alerte)
        
        # Vérification délais
        if projet.date_fin_prevue and projet.statut in ['EN_COURS', 'PLANIFIE']:
            aujourd_hui = timezone.now().date()
            jours_restants = (projet.date_fin_prevue - aujourd_hui).days
            
            # Alerte si dépassement ou proche du dépassement
            if jours_restants <= 0:
                alerte_existante = Alerte.objects.filter(
                    projet=projet,
                    type_alerte='DEPASSEMENT_DELAI',
                    statut__in=['NON_LU', 'LU']
                ).exists()
                
                if not alerte_existante:
                    message = f"Projet en retard de {abs(jours_restants)} jour(s)"
                    alerte = creer_alerte(
                        'DEPASSEMENT_DELAI',
                        'CRITIQUE',
                        message,
                        projet=projet
                    )
                    
                    if alerte:
                        alertes_creees.append(alerte)
            
            elif jours_restants <= 7:  # Alerte 7 jours avant
                alerte_existante = Alerte.objects.filter(
                    projet=projet,
                    type_alerte='ECHEANCE_PROCHE',
                    statut__in=['NON_LU', 'LU']
                ).exists()
                
                if not alerte_existante:
                    message = f"Échéance dans {jours_restants} jour(s)"
                    alerte = creer_alerte(
                        'ECHEANCE_PROCHE',
                        'WARNING',
                        message,
                        projet=projet
                    )
                    
                    if alerte:
                        alertes_creees.append(alerte)
        
        return alertes_creees
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des seuils du projet {projet.id}: {str(e)}")
        return []


def verifier_seuils_operation(operation):
    """
    Vérifier les seuils d'une opération
    """
    alertes_creees = []
    
    try:
        # Récupérer les seuils de l'opération
        seuils = operation.seuils.first()
        
        if seuils and operation.cout_reel:
            niveau_alerte = None
            couleur_seuil = None
            
            # Déterminer le niveau d'alerte basé sur les seuils
            if operation.cout_reel >= seuils.valeur_rouge:
                niveau_alerte = 'CRITIQUE'
                couleur_seuil = 'ROUGE'
            elif operation.cout_reel >= seuils.valeur_jaune:
                niveau_alerte = 'WARNING'
                couleur_seuil = 'JAUNE'
            elif operation.cout_reel <= seuils.valeur_verte:
                couleur_seuil = 'VERT'
            
            if niveau_alerte:
                # Vérifier si une alerte similaire n'existe pas déjà
                alerte_existante = Alerte.objects.filter(
                    operation=operation,
                    type_alerte='DEPASSEMENT_SEUIL',
                    statut__in=['NON_LU', 'LU']
                ).exists()
                
                if not alerte_existante:
                    message = f"Seuil {couleur_seuil} dépassé: {operation.cout_reel}€ (Seuil: {seuils.valeur_rouge if niveau_alerte == 'CRITIQUE' else seuils.valeur_jaune}€)"
                    
                    alerte = creer_alerte(
                        'DEPASSEMENT_SEUIL',
                        niveau_alerte,
                        message,
                        projet=operation.phase.projet,
                        phase=operation.phase,
                        operation=operation
                    )
                    
                    if alerte:
                        alertes_creees.append(alerte)
        
        # Vérifier les délais de l'opération
        if operation.date_fin_prevue and operation.statut in ['EN_COURS', 'PLANIFIE']:
            aujourd_hui = timezone.now().date()
            jours_restants = (operation.date_fin_prevue - aujourd_hui).days
            
            if jours_restants <= 0:
                alerte_existante = Alerte.objects.filter(
                    operation=operation,
                    type_alerte='OPERATION_RETARD',
                    statut__in=['NON_LU', 'LU']
                ).exists()
                
                if not alerte_existante:
                    message = f"Opération en retard de {abs(jours_restants)} jour(s)"
                    alerte = creer_alerte(
                        'OPERATION_RETARD',
                        'CRITIQUE',
                        message,
                        projet=operation.phase.projet,
                        phase=operation.phase,
                        operation=operation
                    )
                    
                    if alerte:
                        alertes_creees.append(alerte)
        
        return alertes_creees
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des seuils de l'opération {operation.id}: {str(e)}")
        return []


def verifier_progression_anormale(projet):
    """
    Vérifier les progressions anormales (progression faible par rapport au temps écoulé)
    """
    alertes_creees = []
    
    try:
        if projet.date_debut and projet.date_fin_prevue:
            aujourd_hui = timezone.now().date()
            duree_totale = (projet.date_fin_prevue - projet.date_debut).days
            duree_ecoulee = (aujourd_hui - projet.date_debut).days
            
            if duree_totale > 0:
                progression_attendue = (duree_ecoulee / duree_totale) * 100
                
                # Calculer la progression moyenne des phases
                phases = projet.phases.all()
                if phases:
                    progression_reelle = sum(phase.progression for phase in phases) / len(phases)
                    
                    # Alerte si la progression réelle est très en retard
                    if progression_reelle < progression_attendue - 20:  # 20% de retard
                        alerte_existante = Alerte.objects.filter(
                            projet=projet,
                            type_alerte='PROGRESSION_FAIBLE',
                            statut__in=['NON_LU', 'LU']
                        ).exists()
                        
                        if not alerte_existante:
                            message = f"Progression faible: {progression_reelle:.1f}% (attendu: {progression_attendue:.1f}%)"
                            alerte = creer_alerte(
                                'PROGRESSION_FAIBLE',
                                'WARNING',
                                message,
                                projet=projet
                            )
                            
                            if alerte:
                                alertes_creees.append(alerte)
        
        return alertes_creees
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de progression du projet {projet.id}: {str(e)}")
        return []


def detecter_toutes_alertes():
    """
    Détecter toutes les alertes automatiquement
    """
    alertes_creees = []
    
    try:
        # Vérifier tous les projets actifs
        projets_actifs = Projet.objects.filter(
            statut__in=['EN_COURS', 'PLANIFIE']
        )
        
        for projet in projets_actifs:
            # Vérifier les seuils du projet
            alertes_creees.extend(verifier_seuils_projet(projet))
            
            # Vérifier la progression
            alertes_creees.extend(verifier_progression_anormale(projet))
            
            # Vérifier les opérations du projet
            operations = Operation.objects.filter(
                phase__projet=projet,
                statut__in=['EN_COURS', 'PLANIFIE']
            )
            
            for operation in operations:
                alertes_creees.extend(verifier_seuils_operation(operation))
        
        logger.info(f"Détection automatique terminée: {len(alertes_creees)} alertes créées")
        return alertes_creees
        
    except Exception as e:
        logger.error(f"Erreur lors de la détection automatique: {str(e)}")
        return []


def envoyer_notification_alerte(alerte):
    """
    Envoyer une notification par email pour une alerte
    """
    try:
        # Déterminer les destinataires
        destinataires = set()
        
        if alerte.projet:
            # Responsable du projet
            if alerte.projet.responsable and alerte.projet.responsable.email:
                destinataires.add(alerte.projet.responsable.email)
            
            # Membres de l'équipe projet avec des rôles spécifiques
            equipe_emails = alerte.projet.membres_equipe.filter(
                role_projet__in=['CHEF_PROJET', 'RESPONSABLE_TECHNIQUE']
            ).values_list('utilisateur__email', flat=True)
            destinataires.update(equipe_emails)
        
        if alerte.operation and alerte.operation.responsable:
            destinataires.add(alerte.operation.responsable.email)
        
        # Ajouter les experts pour les alertes critiques
        if alerte.niveau == 'CRITIQUE':
            from ..models import Utilisateur
            experts_emails = Utilisateur.objects.filter(
                role='EXPERT',
                statut='ACTIF'
            ).values_list('email', flat=True)
            destinataires.update(experts_emails)
        
        # Nettoyer les emails vides
        destinataires = list(filter(None, destinataires))
        
        if destinataires:
            sujet = f"🚨 Alerte {alerte.niveau}: {alerte.type_alerte}"
            
            # Construire le message
            contexte = []
            if alerte.projet:
                contexte.append(f"Projet: {alerte.projet.nom}")
            if alerte.phase:
                contexte.append(f"Phase: {alerte.phase.nom}")
            if alerte.operation:
                contexte.append(f"Opération: {alerte.operation.nom}")
            
            message = f"""
Une nouvelle alerte a été détectée dans le système de monitoring:

📋 DÉTAILS DE L'ALERTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: {alerte.get_type_alerte_display() if hasattr(alerte, 'get_type_alerte_display') else alerte.type_alerte}
Niveau: {alerte.get_niveau_display()}
Message: {alerte.message}
Date/Heure: {alerte.date_alerte.strftime('%d/%m/%Y à %H:%M')}

📍 CONTEXTE
{chr(10).join(contexte) if contexte else 'Aucun contexte spécifique'}

🔗 ACTIONS
Pour traiter cette alerte, connectez-vous au système de monitoring.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ce message est généré automatiquement par le système de monitoring.
            """
            
            send_mail(
                subject=sujet,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinataires,
                fail_silently=True
            )
            
            logger.info(f"Notification envoyée pour l'alerte {alerte.id} à {len(destinataires)} destinataires")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de notification pour l'alerte {alerte.id}: {str(e)}")


def nettoyer_anciennes_alertes(jours=30):
    """
    Nettoyer les anciennes alertes traitées
    """
    try:
        date_limite = timezone.now() - timedelta(days=jours)
        
        anciennes_alertes = Alerte.objects.filter(
            statut='TRAITEE',
            date_alerte__lt=date_limite
        )
        
        count = anciennes_alertes.count()
        anciennes_alertes.delete()
        
        logger.info(f"Nettoyage terminé: {count} anciennes alertes supprimées")
        return count
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des alertes: {str(e)}")
        return 0


def generer_rapport_alertes(date_debut=None, date_fin=None):
    """
    Générer un rapport des alertes pour une période donnée
    """
    try:
        if not date_debut:
            date_debut = timezone.now() - timedelta(days=30)
        if not date_fin:
            date_fin = timezone.now()
        
        alertes = Alerte.objects.filter(
            date_alerte__range=[date_debut, date_fin]
        ).select_related('projet', 'phase', 'operation')
        
        # Statistiques générales
        stats = {
            'total': alertes.count(),
            'par_niveau': {},
            'par_type': {},
            'par_statut': {},
            'par_projet': {}
        }
        
        # Compter par niveau
        for niveau in ['INFO', 'WARNING', 'CRITIQUE']:
            stats['par_niveau'][niveau] = alertes.filter(niveau=niveau).count()
        
        # Compter par type
        types_alertes = alertes.values_list('type_alerte', flat=True).distinct()
        for type_alerte in types_alertes:
            stats['par_type'][type_alerte] = alertes.filter(type_alerte=type_alerte).count()
        
        # Compter par statut
        for statut in ['NON_LU', 'LU', 'TRAITEE']:
            stats['par_statut'][statut] = alertes.filter(statut=statut).count()
        
        # Compter par projet
        projets = alertes.filter(projet__isnull=False).values_list('projet__nom', flat=True)
        for projet_nom in set(projets):
            stats['par_projet'][projet_nom] = alertes.filter(projet__nom=projet_nom).count()
        
        return {
            'periode': {
                'debut': date_debut,
                'fin': date_fin
            },
            'statistiques': stats,
            'alertes_critiques': list(alertes.filter(niveau='CRITIQUE').values(
                'type_alerte', 'message', 'date_alerte', 'projet__nom'
            ))
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        return None