# PteroMonitore/alerts/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

from ..models import Alerte, Projet, Phase, Operation, Utilisateur, Seuil
from .serializers import AlerteSerializer, AlerteCreateSerializer, AlerteUpdateSerializer

logger = logging.getLogger(__name__)


class AlerteListCreateView(generics.ListCreateAPIView):
    """
    Liste et création des alertes
    """
    serializer_class = AlerteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Alerte.objects.select_related(
            'projet', 'phase', 'operation', 'lue_par'
        ).order_by('-date_alerte')
        
        # Filtres
        niveau = self.request.query_params.get('niveau')
        statut = self.request.query_params.get('statut')
        type_alerte = self.request.query_params.get('type_alerte')
        projet_id = self.request.query_params.get('projet')
        
        if niveau:
            queryset = queryset.filter(niveau=niveau)
        if statut:
            queryset = queryset.filter(statut=statut)
        if type_alerte:
            queryset = queryset.filter(type_alerte=type_alerte)
        if projet_id:
            queryset = queryset.filter(projet_id=projet_id)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlerteCreateSerializer
        return AlerteSerializer


class AlerteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détail, mise à jour et suppression d'une alerte
    """
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AlerteUpdateSerializer
        return AlerteSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_alerte_lue(request, pk):
    """
    Marquer une alerte comme lue
    """
    try:
        alerte = Alerte.objects.get(pk=pk)
        alerte.statut = 'LU'
        alerte.lue_par = request.user
        alerte.date_lecture = timezone.now()
        alerte.save()
        
        serializer = AlerteSerializer(alerte)
        return Response(serializer.data)
    except Alerte.DoesNotExist:
        return Response(
            {'error': 'Alerte non trouvée'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_alerte_traitee(request, pk):
    """
    Marquer une alerte comme traitée
    """
    try:
        alerte = Alerte.objects.get(pk=pk)
        alerte.statut = 'TRAITEE'
        if not alerte.lue_par:
            alerte.lue_par = request.user
            alerte.date_lecture = timezone.now()
        alerte.save()
        
        serializer = AlerteSerializer(alerte)
        return Response(serializer.data)
    except Alerte.DoesNotExist:
        return Response(
            {'error': 'Alerte non trouvée'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marquer_toutes_lues(request):
    """
    Marquer toutes les alertes non lues comme lues pour l'utilisateur connecté
    """
    alertes_non_lues = Alerte.objects.filter(statut='NON_LU')
    count = alertes_non_lues.count()
    
    alertes_non_lues.update(
        statut='LU',
        lue_par=request.user,
        date_lecture=timezone.now()
    )
    
    return Response({
        'message': f'{count} alertes marquées comme lues',
        'count': count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistiques_alertes(request):
    """
    Statistiques des alertes
    """
    # Statistiques générales
    total_alertes = Alerte.objects.count()
    alertes_non_lues = Alerte.objects.filter(statut='NON_LU').count()
    alertes_critiques = Alerte.objects.filter(niveau='CRITIQUE').count()
    
    # Alertes par niveau
    alertes_par_niveau = Alerte.objects.values('niveau').annotate(
        count=Count('id')
    ).order_by('niveau')
    
    # Alertes par statut
    alertes_par_statut = Alerte.objects.values('statut').annotate(
        count=Count('id')
    ).order_by('statut')
    
    # Alertes par type
    alertes_par_type = Alerte.objects.values('type_alerte').annotate(
        count=Count('id')
    ).order_by('type_alerte')
    
    # Alertes des 7 derniers jours
    sept_jours = timezone.now() - timedelta(days=7)
    alertes_recentes = Alerte.objects.filter(
        date_alerte__gte=sept_jours
    ).count()
    
    return Response({
        'total_alertes': total_alertes,
        'alertes_non_lues': alertes_non_lues,
        'alertes_critiques': alertes_critiques,
        'alertes_recentes': alertes_recentes,
        'par_niveau': list(alertes_par_niveau),
        'par_statut': list(alertes_par_statut),
        'par_type': list(alertes_par_type)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_alertes(request):
    """
    Historique des alertes avec pagination
    """
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    
    # Filtres pour l'historique
    date_debut = request.query_params.get('date_debut')
    date_fin = request.query_params.get('date_fin')
    projet_id = request.query_params.get('projet')
    
    queryset = Alerte.objects.select_related(
        'projet', 'phase', 'operation', 'lue_par'
    ).order_by('-date_alerte')
    
    if date_debut:
        queryset = queryset.filter(date_alerte__gte=date_debut)
    if date_fin:
        queryset = queryset.filter(date_alerte__lte=date_fin)
    if projet_id:
        queryset = queryset.filter(projet_id=projet_id)
    
    # Pagination manuelle
    start = (page - 1) * page_size
    end = start + page_size
    alertes = queryset[start:end]
    total = queryset.count()
    
    serializer = AlerteSerializer(alertes, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detecter_alertes_automatiques(request):
    """
    Détection automatique des dépassements de seuils
    """
    alertes_detectees = []
    
    try:
        # Vérification des projets
        projets = Projet.objects.filter(statut__in=['EN_COURS', 'PLANIFIE'])
        
        for projet in projets:
            # Alerte dépassement budget
            if (projet.budget_initial and projet.cout_actuel and 
                projet.cout_actuel > projet.budget_initial * (projet.seuil_alerte_cout / 100)):
                
                alerte, created = Alerte.objects.get_or_create(
                    projet=projet,
                    type_alerte='DEPASSEMENT_BUDGET',
                    defaults={
                        'niveau': 'CRITIQUE' if projet.cout_actuel > projet.budget_initial else 'WARNING',
                        'message': f'Dépassement de budget détecté: {projet.cout_actuel}€ / {projet.budget_initial}€'
                    }
                )
                
                if created:
                    alertes_detectees.append(alerte)
                    _envoyer_notification_alerte(alerte)
            
            # Alerte dépassement délai
            if projet.date_fin_prevue and timezone.now().date() > projet.date_fin_prevue:
                alerte, created = Alerte.objects.get_or_create(
                    projet=projet,
                    type_alerte='DEPASSEMENT_DELAI',
                    defaults={
                        'niveau': 'CRITIQUE',
                        'message': f'Projet en retard: Date prévue {projet.date_fin_prevue}'
                    }
                )
                
                if created:
                    alertes_detectees.append(alerte)
                    _envoyer_notification_alerte(alerte)
        
        # Vérification des opérations avec seuils
        operations_ids = Operation.objects.filter(
            statut__in=['EN_COURS', 'PLANIFIE'],
            seuils__isnull=False
        ).values_list('id', flat=True).distinct()

        operations = Operation.objects.filter(id__in=operations_ids)
        
        for operation in operations:
            seuils = operation.seuils.first()
            if seuils and operation.cout_reel:
                niveau_alerte = None
                
                if operation.cout_reel >= seuils.valeur_rouge:
                    niveau_alerte = 'CRITIQUE'
                elif operation.cout_reel >= seuils.valeur_jaune:
                    niveau_alerte = 'WARNING'
                
                if niveau_alerte:
                    alerte, created = Alerte.objects.get_or_create(
                        operation=operation,
                        type_alerte='DEPASSEMENT_SEUIL',
                        defaults={
                            'niveau': niveau_alerte,
                            'message': f'Seuil dépassé pour {operation.nom}: {operation.cout_reel}€'
                        }
                    )
                    
                    if created:
                        alertes_detectees.append(alerte)
                        _envoyer_notification_alerte(alerte)
        
        serializer = AlerteSerializer(alertes_detectees, many=True)
        return Response({
            'message': f'{len(alertes_detectees)} nouvelles alertes détectées',
            'alertes': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la détection d'alertes: {str(e)}")
        return Response(
            {'error': 'Erreur lors de la détection d\'alertes'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _envoyer_notification_alerte(alerte):
    """
    Envoyer une notification par email pour une alerte
    """
    try:
        # Déterminer les destinataires
        destinataires = []
        
        if alerte.projet:
            # Responsable du projet
            if alerte.projet.responsable and alerte.projet.responsable.email:
                destinataires.append(alerte.projet.responsable.email)
            
            # Membres de l'équipe projet
            equipe_emails = alerte.projet.membres_equipe.values_list(
                'utilisateur__email', flat=True
            )
            destinataires.extend(list(equipe_emails))
        
        if alerte.operation and alerte.operation.responsable:
            destinataires.append(alerte.operation.responsable.email)
        
        # Supprimer les doublons
        destinataires = list(set(filter(None, destinataires)))
        
        if destinataires:
            sujet = f"Alerte {alerte.niveau}: {alerte.type_alerte}"
            message = f"""
            Une nouvelle alerte a été détectée:
            
            Type: {alerte.type_alerte}
            Niveau: {alerte.niveau}
            Message: {alerte.message}
            Date: {alerte.date_alerte}
            
            Projet: {alerte.projet.nom if alerte.projet else 'N/A'}
            Phase: {alerte.phase.nom if alerte.phase else 'N/A'}
            Opération: {alerte.operation.nom if alerte.operation else 'N/A'}
            """
            
            send_mail(
                subject=sujet,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinataires,
                fail_silently=True
            )
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de notification: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alertes_tableau_bord(request):
    """
    Alertes pour le tableau de bord
    """
    # Alertes critiques récentes
    alertes_critiques = Alerte.objects.filter(
        niveau='CRITIQUE',
        statut__in=['NON_LU', 'LU']
    ).select_related('projet', 'phase', 'operation').order_by('-date_alerte')[:5]
    
    # Alertes non lues
    alertes_non_lues = Alerte.objects.filter(
        statut='NON_LU'
    ).select_related('projet', 'phase', 'operation').order_by('-date_alerte')[:10]
    
    # Résumé par niveau
    resume_niveaux = Alerte.objects.aggregate(
        critiques=Count('id', filter=Q(niveau='CRITIQUE')),
        warnings=Count('id', filter=Q(niveau='WARNING')),
        infos=Count('id', filter=Q(niveau='INFO'))
    )
    
    return Response({
        'alertes_critiques': AlerteSerializer(alertes_critiques, many=True).data,
        'alertes_non_lues': AlerteSerializer(alertes_non_lues, many=True).data,
        'resume_niveaux': resume_niveaux,
        'total_non_lues': alertes_non_lues.count()
    })