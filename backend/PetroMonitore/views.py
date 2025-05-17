from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status, generics, permissions,viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from decimal import Decimal
from django.db.models import Avg,Sum
from django.http import Http404  
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser
from django.utils import timezone
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Projet, Utilisateur, Phase, Operation,EquipeProjet,HistoriqueModification, Seuil,Rapport
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    ProjetSerializer,
    ProjetCreateSerializer,
    ProjetUpdateSerializer,
    ProjetDetailSerializer,
    PhaseSerializer, 
    PhaseCreateSerializer, 
    PhaseUpdateSerializer,
    OperationSerializer, 
    OperationCreateSerializer, 
    OperationUpdateSerializer,
    SeuilSerializer, 
    HistoriqueModificationSeuilSerializer,
    PhaseDetailStatusSerializer,
    ProjetDetailStatusSerializer,
)
from .permissions import IsAdminUser
from .authentication import UtilisateurBackend
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction

from .utils import (
    update_phase_progress, 
    update_project_costs, 
    update_phase_costs,
    evaluer_statut_couleur_phase,
    evaluer_statut_couleur_projet,
    get_tokens_for_user
)

class LoginView(APIView):
    authentication_classes = []  # No auth needed for login
    permission_classes = []  # No permissions needed for login

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('mot_de_passe')
        
        user = UtilisateurBackend().authenticate(
            request,
            username=email,
            password=password
        )

        if user is None:
            return Response({'error': 'Invalid credentials or inactive account'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        })

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        users = Utilisateur.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        user = self.get_object(pk)
        if request.user != user and not request.user.role == 'TOP_MANAGEMENT':
            return Response(
                {'error': 'Vous n\'avez pas la permission'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = self.get_object(pk)
        if request.user != user and not request.user.role == 'TOP_MANAGEMENT':
            return Response(
                {'error': 'Vous n\'avez pas la permission'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not request.user.role == 'TOP_MANAGEMENT':
            return Response(
                {'error': 'Vous n\'avez pas la permission'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self, pk):
        try:
            return Utilisateur.objects.get(pk=pk)
        except Utilisateur.DoesNotExist:
            raise Http404

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Ancien mot de passe incorrect'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.mot_de_passe = make_password(serializer.validated_data['new_password'])

            user.save()
            return Response({'message': 'Mot de passe mis à jour avec succès'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Déconnexion réussie'}, 
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {'error': f'Invalid token: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
class ProjetListView(APIView):
    """
    Liste tous les projets ou crée un nouveau projet
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste tous les projets avec possibilité de filtrage
        """
        projets = Projet.objects.all()
        
        # Filtrage par statut
        statut = request.query_params.get('statut', None)
        if statut:
            projets = projets.filter(statut=statut)
        
        # Filtrage par responsable
        responsable_id = request.query_params.get('responsable', None)
        if responsable_id:
            projets = projets.filter(responsable_id=responsable_id)
        
        # Filtrage par date de début (après une date)
        date_debut_apres = request.query_params.get('date_debut_apres', None)
        if date_debut_apres:
            projets = projets.filter(date_debut__gte=date_debut_apres)
        
        # Filtrage par date de fin (avant une date)
        date_fin_avant = request.query_params.get('date_fin_avant', None)
        if date_fin_avant:
            projets = projets.filter(date_fin_prevue__lte=date_fin_avant)
        
        serializer = ProjetSerializer(projets, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Crée un nouveau projet
        """
        if not request.user.role == 'TOP_MANAGEMENT' and not request.user.role == 'EXPERT':
            return Response(
                {'error': 'Vous n\'avez pas la permission de créer un projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = ProjetCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjetDetailView(APIView):
    """
    Récupération, mise à jour ou suppression d'un projet
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """
        Récupère un objet projet avec sa clé primaire
        """
        try:
            return Projet.objects.get(pk=pk)
        except Projet.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        """
        Récupère les détails d'un projet
        """
        projet = self.get_object(pk)
        serializer = ProjetDetailSerializer(projet)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Met à jour un projet existant
        """
        projet = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier ce projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProjetUpdateSerializer(projet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Calculer le coût actuel basé sur les phases
            self.update_cout_actuel(projet)
            
            return Response(ProjetDetailSerializer(projet).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Supprime un projet
        """
        if not request.user.role == 'TOP_MANAGEMENT':
            return Response(
                {'error': 'Seul le Top Management peut supprimer un projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        projet = self.get_object(pk)
        projet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update_cout_actuel(self, projet):
        """
        Calcule et met à jour le coût actuel d'un projet basé sur les coûts des phases
        """
        cout_total = projet.phases.aggregate(total=Sum('cout_actuel'))['total'] or Decimal('0.00')
        projet.cout_actuel = cout_total
        projet.save(update_fields=['cout_actuel'])


class ProjetStatutView(APIView):
    """
    Mise à jour du statut d'un projet
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Projet.objects.get(pk=pk)
        except Projet.DoesNotExist:
            raise Http404
    
    def post(self, request, pk):
        """
        Met à jour le statut d'un projet
        """
        projet = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier le statut de ce projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        nouveau_statut = request.data.get('statut')
        if not nouveau_statut:
            return Response(
                {'error': 'Le statut est requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si le statut est valide
        if nouveau_statut not in [choice[0] for choice in Projet.STATUT_CHOICES]:
            return Response(
                {'error': 'Statut invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        projet.statut = nouveau_statut
        projet.save(update_fields=['statut'])
        
        return Response({'message': 'Statut mis à jour avec succès'})


class ProjetResponsableView(APIView):
    """
    Affectation d'un responsable à un projet
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Projet.objects.get(pk=pk)
        except Projet.DoesNotExist:
            raise Http404
    
    def post(self, request, pk):
        """
        Affecte un responsable au projet
        """
        if not request.user.role == 'TOP_MANAGEMENT':
            return Response(
                {'error': 'Seul le Top Management peut affecter un responsable'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        projet = self.get_object(pk)
        responsable_id = request.data.get('responsable_id')
        
        if not responsable_id:
            return Response(
                {'error': 'L\'ID du responsable est requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            responsable = Utilisateur.objects.get(pk=responsable_id)
        except Utilisateur.DoesNotExist:
            return Response(
                {'error': 'Utilisateur non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que l'utilisateur a un rôle compatible
        if responsable.role not in ['EXPERT', 'TOP_MANAGEMENT']:
            return Response(
                {'error': 'Seuls les experts et le top management peuvent être responsables de projets'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        projet.responsable = responsable
        projet.save(update_fields=['responsable'])
        
        return Response({'message': 'Responsable affecté avec succès'})
    
    
class PhaseListView(APIView):
    """
    Liste et création des phases pour un projet
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, projet_id):
        """
        Récupère toutes les phases d'un projet
        """
        try:
            projet = Projet.objects.get(pk=projet_id)
        except Projet.DoesNotExist:
            return Response({'error': 'Projet non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de voir les phases de ce projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        phases = Phase.objects.filter(projet=projet).order_by('ordre')
        serializer = PhaseSerializer(phases, many=True)
        return Response(serializer.data)
    
    def post(self, request, projet_id):
        """
        Crée une nouvelle phase pour un projet
        """
        try:
            projet = Projet.objects.get(pk=projet_id)
        except Projet.DoesNotExist:
            return Response({'error': 'Projet non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de créer des phases pour ce projet'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ajouter le projet au context de données
        data = request.data.copy()
        data['projet'] = projet_id
        
        serializer = PhaseCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhaseDetailView(APIView):
    """
    Récupération, mise à jour et suppression d'une phase
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """
        Récupère un objet phase
        """
        try:
            return Phase.objects.get(pk=pk)
        except Phase.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        """
        Récupère les détails d'une phase
        """
        phase = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de voir cette phase'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PhaseSerializer(phase)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Met à jour une phase
        """
        phase = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier cette phase'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PhaseUpdateSerializer(phase, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Mise à jour de la progression et des coûts du projet
            self.update_projet_progression(phase.projet)
            
            return Response(PhaseSerializer(phase).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Supprime une phase
        """
        phase = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de supprimer cette phase'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        phase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update_projet_progression(self, projet):
        """
        Calcule et met à jour la progression globale du projet
        """
        # Calcul de la progression moyenne des phases
        phases_progression = projet.phases.aggregate(
            avg_progression=Avg('progression'),
            total_cout_actuel=Sum('cout_actuel') or Decimal('0.00'),
            total_budget_alloue=Sum('budget_alloue') or Decimal('0.00')
        )
        
        projet.cout_actuel = phases_progression['total_cout_actuel']
        projet.save(update_fields=['cout_actuel'])


class PhaseOrderingView(APIView):
    """
    Gestion de l'ordonnancement des phases
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, projet_id):
        """
        Réordonne les phases d'un projet
        """
        try:
            projet = Projet.objects.get(pk=projet_id)
        except Projet.DoesNotExist:
            return Response({'error': 'Projet non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de réordonner les phases'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Format attendu : [{'id': phase_id, 'ordre': new_ordre}, ...]
        phases_order = request.data.get('phases', [])
        
        # Validation et mise à jour des ordres
        for phase_data in phases_order:
            try:
                phase = Phase.objects.get(pk=phase_data['id'], projet=projet)
                phase.ordre = phase_data['ordre']
                phase.save(update_fields=['ordre'])
            except (Phase.DoesNotExist, KeyError):
                return Response({
                    'error': f'Phase invalide : {phase_data}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupération des phases mises à jour
        phases = Phase.objects.filter(projet=projet).order_by('ordre')
        serializer = PhaseSerializer(phases, many=True)
        return Response(serializer.data)


class OperationListView(APIView):
    """
    Liste et création des opérations pour une phase
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, phase_id):
        """
        Récupère toutes les opérations d'une phase
        """
        try:
            phase = Phase.objects.get(pk=phase_id)
        except Phase.DoesNotExist:
            return Response({'error': 'Phase non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de voir les opérations de cette phase'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        operations = Operation.objects.filter(phase=phase).order_by('date_debut_prevue')
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)
    
    def post(self, request, phase_id):
        """
        Crée une nouvelle opération dans une phase
        """
        try:
            phase = Phase.objects.get(pk=phase_id)
        except Phase.DoesNotExist:
            return Response({'error': 'Phase non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de créer des opérations pour cette phase'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ajouter la phase au context de données
        data = request.data.copy()
        data['phase'] = phase_id
        
        serializer = OperationCreateSerializer(data=data)
        if serializer.is_valid():
            operation = serializer.save()
            
            # Mettre à jour la progression de la phase
            self.update_phase_progression(phase)
            
            return Response(OperationSerializer(operation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_phase_progression(self, phase):
        """
        Calcule et met à jour la progression globale de la phase
        """
        operations = Operation.objects.filter(phase=phase)
        
        # Calcul de la progression moyenne des opérations
        total_progression = operations.aggregate(
            avg_progression=Avg('progression'),
            total_cout_reel=Sum('cout_reel') or Decimal('0.00')
        )
        
        phase.progression = total_progression['avg_progression'] or Decimal('0.00')
        phase.cout_actuel = total_progression['total_cout_reel']
        phase.save(update_fields=['progression', 'cout_actuel'])
        
        # Mise à jour de la progression du projet
        PhaseDetailView().update_projet_progression(phase.projet)



class OperationDetailView(APIView):
    """
    Récupération, mise à jour et suppression d'une opération
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """
        Récupère un objet opération
        """
        try:
            return Operation.objects.get(pk=pk)
        except Operation.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        """
        Récupère les détails d'une opération
        """
        operation = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != operation.phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de voir cette opération'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OperationSerializer(operation)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Met à jour une opération
        """
        operation = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != operation.phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier cette opération'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OperationUpdateSerializer(operation, data=request.data, partial=True)
        if serializer.is_valid():
            operation = serializer.save()
            
            # Mise à jour de la progression de la phase
            OperationListView().update_phase_progression(operation.phase)
            
            return Response(OperationSerializer(operation).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Supprime une opération
        """
        operation = self.get_object(pk)
        
        # Vérification des permissions
        if not request.user.role == 'TOP_MANAGEMENT' and request.user != operation.phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de supprimer cette opération'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Sauvegarder la phase avant suppression pour mise à jour
        phase = operation.phase
        operation.delete()
        
        # Mettre à jour la progression de la phase
        OperationListView().update_phase_progression(phase)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class OperationOrderingView(APIView):
    """
    Gestion de l'ordonnancement des opérations
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, phase_id):
        """
        Réordonne les opérations d'une phase
        """
        try:
            phase = Phase.objects.get(pk=phase_id)
        except Phase.DoesNotExist:
            return Response({'error': 'Phase non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de réordonner les opérations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Format attendu : [{'id': operation_id, 'date_debut_prevue': new_date}, ...]
        operations_order = request.data.get('operations', [])
        
        # Validation et mise à jour des dates/ordres
        for operation_data in operations_order:
            try:
                operation = Operation.objects.get(pk=operation_data['id'], phase=phase)
                
                # Mettre à jour la date de début si fournie
                if 'date_debut_prevue' in operation_data:
                    operation.date_debut_prevue = operation_data['date_debut_prevue']
                
                # Mettre à jour l'ordre si fourni
                if 'ordre' in operation_data:
                    operation.ordre = operation_data['ordre']
                
                operation.save()
            except (Operation.DoesNotExist, KeyError):
                return Response({
                    'error': f'Opération invalide : {operation_data}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupération des opérations mises à jour
        operations = Operation.objects.filter(phase=phase).order_by('date_debut_prevue')
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)


class OperationProgressionView(APIView):
    """
    Mise à jour manuelle de la progression d'une opération
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """
        Met à jour la progression d'une opération
        """
        try:
            operation = Operation.objects.get(pk=pk)
        except Operation.DoesNotExist:
            return Response({'error': 'Opération non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérification des permissions
        if not request.user.role in ['TOP_MANAGEMENT', 'EXPERT'] and request.user != operation.phase.projet.responsable:
            return Response(
                {'error': 'Vous n\'avez pas la permission de modifier la progression de cette opération'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validation de la progression
        progression = request.data.get('progression')
        if progression is None:
            return Response({'error': 'La progression est requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            progression = float(progression)
            if progression < 0 or progression > 100:
                raise ValueError("Progression doit être entre 0 et 100")
        except ValueError:
            return Response({'error': 'Progression invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mise à jour de la progression
        operation.progression = progression
        
        # Mettre à jour les dates réelles si la progression change
        if progression > 0 and not operation.date_debut_reelle:
            operation.date_debut_reelle = timezone.now().date()
        
        if progression == 100 and not operation.date_fin_reelle:
            operation.date_fin_reelle = timezone.now().date()
        
        operation.save()
        
        # Mettre à jour la progression de la phase
        OperationListView().update_phase_progression(operation.phase)
        
        return Response(OperationSerializer(operation).data)
    
class EquipeProjetListCreate(generics.ListCreateAPIView):
    """
    API endpoint pour lister tous les membres d'équipe ou en créer un nouveau.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = EquipeProjet.objects.all()
        
        # Filtrage par projet
        projet_id = self.request.query_params.get('projet')
        if projet_id:
            queryset = queryset.filter(projet_id=projet_id)
            
        # Filtrage par utilisateur
        utilisateur_id = self.request.query_params.get('utilisateur')
        if utilisateur_id:
            queryset = queryset.filter(utilisateur_id=utilisateur_id)
            
        # Filtrage par rôle
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role_projet__icontains=role)
            
        return queryset
    
    def get_serializer_class(self):
        from .serializers import EquipeProjetSerializer
        return EquipeProjetSerializer
    
    def perform_create(self, serializer):
        with transaction.atomic():
            # Enregistrement de l'affectation
            membre = serializer.save(affecte_par=self.request.user)
            
            # Enregistrement dans l'historique
            HistoriqueModification.objects.create(
                table_modifiee='EquipeProjet',
                id_enregistrement=membre.id,
                champ_modifie='creation',
                nouvelle_valeur=f'Utilisateur {membre.utilisateur.id} affecté au projet {membre.projet.id} avec le rôle {membre.role_projet}',
                modifie_par=self.request.user,
                commentaire='Création d\'une affectation d\'équipe'
            )

class EquipeProjetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint pour récupérer, mettre à jour ou supprimer un membre d'équipe spécifique.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EquipeProjet.objects.all()
    
    def get_serializer_class(self):
        from .serializers import EquipeProjetSerializer
        return EquipeProjetSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Sauvegarde des anciennes valeurs pour l'historique
        old_role = instance.role_projet
        
        with transaction.atomic():
            response = super().update(request, *args, **kwargs)
            
            # Enregistrement dans l'historique si le rôle a changé
            if old_role != instance.role_projet:
                HistoriqueModification.objects.create(
                    table_modifiee='EquipeProjet',
                    id_enregistrement=instance.id,
                    champ_modifie='role_projet',
                    ancienne_valeur=old_role,
                    nouvelle_valeur=instance.role_projet,
                    modifie_par=request.user,
                    commentaire='Modification du rôle dans l\'équipe'
                )
                
            return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        with transaction.atomic():
            # Enregistrement dans l'historique avant suppression
            HistoriqueModification.objects.create(
                table_modifiee='EquipeProjet',
                id_enregistrement=instance.id,
                champ_modifie='suppression',
                ancienne_valeur=f'Utilisateur {instance.utilisateur.id} affecté au projet {instance.projet.id} avec le rôle {instance.role_projet}',
                modifie_par=request.user,
                commentaire='Désaffectation d\'un membre de l\'équipe'
            )
            
            return super().destroy(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def projet_membres(request, projet_id):
    """
    API endpoint pour récupérer tous les membres d'un projet spécifique.
    """
    projet = get_object_or_404(Projet, pk=projet_id)
    membres = EquipeProjet.objects.filter(projet=projet)
    
    from .serializers import EquipeProjetDetailSerializer
    serializer = EquipeProjetDetailSerializer(membres, many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def affecter_utilisateur(request):
    """
    API endpoint pour affecter un utilisateur à un projet avec un rôle spécifique.
    """
    projet_id = request.data.get('projet_id')
    utilisateur_id = request.data.get('utilisateur_id')
    role_projet = request.data.get('role_projet')
    
    if not all([projet_id, utilisateur_id, role_projet]):
        return Response(
            {"error": "Les champs projet_id, utilisateur_id et role_projet sont obligatoires"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    projet = get_object_or_404(Projet, pk=projet_id)
    utilisateur = get_object_or_404(Utilisateur, pk=utilisateur_id)
    
    # Vérifier si l'utilisateur est déjà membre de l'équipe
    if EquipeProjet.objects.filter(projet=projet, utilisateur=utilisateur).exists():
        return Response(
            {"error": "L'utilisateur est déjà membre de l'équipe de ce projet"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Création de l'affectation
        equipe = EquipeProjet.objects.create(
            projet=projet,
            utilisateur=utilisateur,
            role_projet=role_projet,
            affecte_par=request.user
        )
        
        # Enregistrement dans l'historique
        HistoriqueModification.objects.create(
            table_modifiee='EquipeProjet',
            id_enregistrement=equipe.id,
            champ_modifie='creation',
            nouvelle_valeur=f'Utilisateur {utilisateur.id} affecté au projet {projet.id} avec le rôle {role_projet}',
            modifie_par=request.user,
            commentaire='Affectation d\'un utilisateur à un projet'
        )
    
    from .serializers import EquipeProjetSerializer
    serializer = EquipeProjetSerializer(equipe)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def desaffecter_utilisateur(request, equipe_id):
    """
    API endpoint pour désaffecter un utilisateur d'un projet.
    """
    equipe = get_object_or_404(EquipeProjet, pk=equipe_id)
    
    with transaction.atomic():
        # Enregistrement dans l'historique avant suppression
        HistoriqueModification.objects.create(
            table_modifiee='EquipeProjet',
            id_enregistrement=equipe.id,
            champ_modifie='suppression',
            ancienne_valeur=f'Utilisateur {equipe.utilisateur.id} affecté au projet {equipe.projet.id} avec le rôle {equipe.role_projet}',
            modifie_par=request.user,
            commentaire='Désaffectation d\'un utilisateur d\'un projet'
        )
        
        # Suppression de l'affectation
        equipe.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


class SeuilListCreateView(ListCreateAPIView):
    """
    Vue pour lister tous les seuils et en créer un nouveau
    """
    queryset = Seuil.objects.all()
    serializer_class = SeuilSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['operation__nom']
    ordering_fields = ['date_definition', 'date_modification']
    
    def perform_create(self, serializer):
        """
        Création d'un nouveau seuil avec enregistrement du créateur
        """
        with transaction.atomic():
            # Enregistrer le seuil avec l'utilisateur courant comme créateur
            seuil = serializer.save(
                defini_par=self.request.user,
                date_definition=timezone.now()
            )
            
            # Enregistrer dans l'historique
            HistoriqueModification.objects.create(
                table_modifiee='Seuil',
                id_enregistrement=seuil.id,
                champ_modifie='création',
                nouvelle_valeur=f"Vert: {seuil.valeur_verte}, Jaune: {seuil.valeur_jaune}, Rouge: {seuil.valeur_rouge}",
                modifie_par=self.request.user,
                commentaire="Création initiale du seuil"
            )


class SeuilDetailView(RetrieveUpdateDestroyAPIView):
    """
    Vue pour récupérer, modifier ou supprimer un seuil spécifique
    """
    queryset = Seuil.objects.all()
    serializer_class = SeuilSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """
        Modification d'un seuil avec enregistrement des modifications
        """
        with transaction.atomic():
            # Récupérer l'objet avant modification
            ancien_seuil = Seuil.objects.get(pk=serializer.instance.pk)
            anciennes_valeurs = {
                'valeur_verte': ancien_seuil.valeur_verte,
                'valeur_jaune': ancien_seuil.valeur_jaune,
                'valeur_rouge': ancien_seuil.valeur_rouge
            }
            
            # Enregistrer les modifications
            seuil = serializer.save(
                modifie_par=self.request.user,
                date_modification=timezone.now()
            )
            
            # Pour chaque champ modifié, créer une entrée dans l'historique
            for champ, ancienne_valeur in anciennes_valeurs.items():
                nouvelle_valeur = getattr(seuil, champ)
                if ancienne_valeur != nouvelle_valeur:
                    HistoriqueModification.objects.create(
                        table_modifiee='Seuil',
                        id_enregistrement=seuil.id,
                        champ_modifie=champ,
                        ancienne_valeur=str(ancienne_valeur),
                        nouvelle_valeur=str(nouvelle_valeur),
                        modifie_par=self.request.user,
                        commentaire=f"Modification du seuil {champ}"
                    )


class SeuilHistoriqueView(APIView):
    """
    Vue pour récupérer l'historique des modifications d'un seuil spécifique
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Retourne l'historique des modifications pour un seuil spécifique
        """
        historique = HistoriqueModification.objects.filter(
            table_modifiee='Seuil',
            id_enregistrement=pk
        ).order_by('-date_modification')
        
        serializer = HistoriqueModificationSeuilSerializer(historique, many=True)
        return Response(serializer.data)


class SeuilOperationView(APIView):
    """
    Vue pour récupérer les seuils pour une opération donnée
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, operation_id, *args, **kwargs):
        """
        Retourne les seuils pour une opération donnée
        """
        if not operation_id:
            return Response(
                {"error": "Le paramètre operation_id est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            seuil = Seuil.objects.get(operation_id=operation_id)
            serializer = SeuilSerializer(seuil)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Seuil.DoesNotExist:
            return Response(
                {"error": f"Aucun seuil défini pour l'opération avec ID {operation_id}"},
                status=status.HTTP_404_NOT_FOUND
            )   

class SeuilInitialiserOperationView(APIView):
    """
    Vue pour initialiser les seuils pour une opération donnée
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Initialise les seuils pour une opération donnée
        """
        operation_id = request.data.get('operation_id')
        valeur_verte = request.data.get('valeur_verte')
        valeur_jaune = request.data.get('valeur_jaune')
        valeur_rouge = request.data.get('valeur_rouge')
        
        if not all([operation_id, valeur_verte, valeur_jaune, valeur_rouge]):
            return Response(
                {"error": "Tous les paramètres sont requis: operation_id, valeur_verte, valeur_jaune, valeur_rouge"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            operation = Operation.objects.get(pk=operation_id)
        except Operation.DoesNotExist:
            return Response(
                {"error": f"Opération avec ID {operation_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier si les seuils sont déjà définis pour cette opération
        existing_seuil = Seuil.objects.filter(operation=operation).first()
        if existing_seuil:
            return Response(
                {"error": f"Des seuils existent déjà pour cette opération. Utilisez la méthode PUT pour les modifier."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            seuil = Seuil.objects.create(
                operation=operation,
                valeur_verte=valeur_verte,
                valeur_jaune=valeur_jaune,
                valeur_rouge=valeur_rouge,
                defini_par=request.user,
                date_definition=timezone.now()
            )
            
            HistoriqueModification.objects.create(
                table_modifiee='Seuil',
                id_enregistrement=seuil.id,
                champ_modifie='création',
                nouvelle_valeur=f"Vert: {seuil.valeur_verte}, Jaune: {seuil.valeur_jaune}, Rouge: {seuil.valeur_rouge}",
                modifie_par=request.user,
                commentaire="Initialisation des seuils pour l'opération"
            )
            
            serializer = SeuilSerializer(seuil)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class HistoriqueSeuilListView(ListAPIView):
    """
    Vue pour lister l'historique des modifications de seuils
    """
    serializer_class = HistoriqueModificationSeuilSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['table_modifiee', 'champ_modifie', 'commentaire']
    ordering_fields = ['date_modification']
    
    def get_queryset(self):
        """
        Limite l'historique aux modifications de seuils uniquement
        """
        return HistoriqueModification.objects.filter(
            table_modifiee='Seuil'
        ).order_by('-date_modification')


class HistoriqueSeuilDetailView(RetrieveAPIView):
    """
    Vue pour récupérer un enregistrement d'historique spécifique
    """
    serializer_class = HistoriqueModificationSeuilSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Limite l'historique aux modifications de seuils uniquement
        """
        return HistoriqueModification.objects.filter(
            table_modifiee='Seuil'
        )
        
        
class PhaseStatusView(APIView):
    """
    Vue pour récupérer les informations de statut d'une phase
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, phase_id):
        """
        Retourne les informations de statut pour une phase spécifique
        """
        try:
            phase = Phase.objects.get(pk=phase_id)
            
            # Mettre à jour la progression et le coût de la phase
            update_phase_progress(phase_id)
            update_phase_costs(phase_id)
            
            # Récupérer la phase actualisée
            phase = Phase.objects.get(pk=phase_id)
            
            # Sérialiser les données
            serializer = PhaseDetailStatusSerializer(phase)
            
            return Response(serializer.data)
        except Phase.DoesNotExist:
            return Response(
                {"error": f"Phase avec ID {phase_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )


class ProjetStatusView(APIView):
    """
    Vue pour récupérer les informations de statut d'un projet
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, projet_id):
        """
        Retourne les informations de statut pour un projet spécifique
        """
        try:
            projet = Projet.objects.get(pk=projet_id)
            
            # Mettre à jour les coûts du projet
            update_project_costs(projet_id)
            
            # Mettre à jour la progression pour chaque phase du projet
            phases = projet.phases.all()
            for phase in phases:
                update_phase_progress(phase.id)
                update_phase_costs(phase.id)
            
            # Récupérer le projet actualisé
            projet = Projet.objects.get(pk=projet_id)
            
            # Sérialiser les données
            serializer = ProjetDetailStatusSerializer(projet)
            
            return Response(serializer.data)
        except Projet.DoesNotExist:
            return Response(
                {"error": f"Projet avec ID {projet_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )


class OperationStatusUpdateView(APIView):
    """
    Vue pour mettre à jour une opération et propager les changements
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, operation_id):
        """
        Mise à jour d'une opération et propagation des changements aux phases et projets
        """
        from .serializers import OperationUpdateSerializer
        
        try:
            operation = Operation.objects.get(pk=operation_id)
        except Operation.DoesNotExist:
            return Response(
                {"error": f"Opération avec ID {operation_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OperationUpdateSerializer(operation, data=request.data, partial=True)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Sauvegarder les modifications de l'opération
                serializer.save()
                
                # Mettre à jour la phase parente
                phase_id = operation.phase.id
                update_phase_progress(phase_id)
                update_phase_costs(phase_id)
                
                # Mettre à jour le projet parent
                projet_id = operation.phase.projet.id
                update_project_costs(projet_id)
                
                # Récupérer l'opération mise à jour
                operation = Operation.objects.get(pk=operation_id)
                
                # Sérialiser avec le statut couleur
                from .serializers import OperationStatusSerializer
                result_serializer = OperationStatusSerializer(operation)
                
                return Response(result_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhaseProgressUpdateView(APIView):
    """
    Vue pour recalculer et mettre à jour la progression d'une phase
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, phase_id):
        """
        Recalcule et met à jour la progression d'une phase
        """
        try:
            phase = Phase.objects.get(pk=phase_id)
        except Phase.DoesNotExist:
            return Response(
                {"error": f"Phase avec ID {phase_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            # Mettre à jour la progression et les coûts
            success_progress = update_phase_progress(phase_id)
            success_costs = update_phase_costs(phase_id)
            
            if not (success_progress and success_costs):
                return Response(
                    {"error": "Erreur lors de la mise à jour de la phase"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Récupérer la phase mise à jour
            phase = Phase.objects.get(pk=phase_id)
            
            # Sérialiser avec le statut couleur
            serializer = PhaseDetailStatusSerializer(phase)
            
            return Response(serializer.data)


class ProjetProgressUpdateView(APIView):
    """
    Vue pour recalculer et mettre à jour la progression et les coûts d'un projet
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, projet_id):
        """
        Recalcule et met à jour la progression et les coûts d'un projet
        """
        try:
            projet = Projet.objects.get(pk=projet_id)
        except Projet.DoesNotExist:
            return Response(
                {"error": f"Projet avec ID {projet_id} n'existe pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            # Mettre à jour les coûts du projet
            success_costs = update_project_costs(projet_id)
            
            if not success_costs:
                return Response(
                    {"error": "Erreur lors de la mise à jour des coûts du projet"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Mettre à jour toutes les phases du projet
            phases = projet.phases.all()
            for phase in phases:
                update_phase_progress(phase.id)
                update_phase_costs(phase.id)
            
            # Récupérer le projet mis à jour
            projet = Projet.objects.get(pk=projet_id)
            
            # Sérialiser avec le statut couleur
            serializer = ProjetDetailStatusSerializer(projet)
            
            return Response(serializer.data)
        
