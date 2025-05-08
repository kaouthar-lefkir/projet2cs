from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import Http404  
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import Utilisateur
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer
)
from .permissions import IsAdminUser
from .authentication import UtilisateurBackend
from .serializers import UserSerializer  
from .utils import get_tokens_for_user 

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