from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from ..models import Probleme, Solution
from .serializers import (
    ProblemeListSerializer, 
    ProblemeCreateSerializer, 
    ProblemeUpdateSerializer,
    ProblemeDetailSerializer,
    SolutionListSerializer,
    SolutionCreateSerializer,
    SolutionUpdateSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProblemeListView(APIView):
    """Vue pour lister et créer des problèmes"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Récupérer la liste des problèmes avec filtres"""
        problemes = Probleme.objects.all().order_by('-date_signalement')

        # Appliquer des filtres si présents dans la requête
        projet_id = request.query_params.get('projet')
        if projet_id:
            problemes = problemes.filter(projet_id=projet_id)

        phase_id = request.query_params.get('phase')
        if phase_id:
            problemes = problemes.filter(phase_id=phase_id)

        operation_id = request.query_params.get('operation')
        if operation_id:
            problemes = problemes.filter(operation_id=operation_id)

        gravite = request.query_params.get('gravite')
        if gravite:
            problemes = problemes.filter(gravite=gravite)

        statut = request.query_params.get('statut')
        if statut:
            problemes = problemes.filter(statut=statut)

        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(problemes, request)
        
        serializer = ProblemeListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Créer un nouveau problème"""
        serializer = ProblemeCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            probleme = serializer.save()
            return Response(
                ProblemeListSerializer(probleme).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemeDetailView(APIView):
    """Vue pour récupérer, modifier ou supprimer un problème spécifique"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Récupérer les détails d'un problème"""
        probleme = get_object_or_404(Probleme, pk=pk)
        serializer = ProblemeDetailSerializer(probleme)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Mettre à jour un problème"""
        probleme = get_object_or_404(Probleme, pk=pk)
        serializer = ProblemeUpdateSerializer(probleme, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Retourner une représentation complète du problème mis à jour
            return Response(ProblemeDetailSerializer(probleme).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Supprimer un problème"""
        probleme = get_object_or_404(Probleme, pk=pk)
        probleme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SolutionListView(APIView):
    """Vue pour lister et créer des solutions"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Récupérer la liste des solutions avec filtres"""
        solutions = Solution.objects.all().order_by('-date_proposition')

        # Appliquer des filtres si présents dans la requête
        probleme_id = request.query_params.get('probleme')
        if probleme_id:
            solutions = solutions.filter(probleme_id=probleme_id)

        statut = request.query_params.get('statut')
        if statut:
            solutions = solutions.filter(statut=statut)

        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(solutions, request)
        
        serializer = SolutionListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Créer une nouvelle solution"""
        serializer = SolutionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            solution = serializer.save()
            return Response(
                SolutionListSerializer(solution).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SolutionDetailView(APIView):
    """Vue pour récupérer, modifier ou supprimer une solution spécifique"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Récupérer les détails d'une solution"""
        solution = get_object_or_404(Solution, pk=pk)
        serializer = SolutionListSerializer(solution)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Mettre à jour une solution"""
        solution = get_object_or_404(Solution, pk=pk)
        serializer = SolutionUpdateSerializer(solution, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Retourner une représentation complète de la solution mise à jour
            return Response(SolutionListSerializer(solution).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Supprimer une solution"""
        solution = get_object_or_404(Solution, pk=pk)
        solution.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProblemesByEntityView(APIView):
    """Vue pour récupérer les problèmes liés à une entité (projet, phase, opération)"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, entity_type, entity_id):
        """
        Récupérer les problèmes liés à une entité spécifique
        entity_type peut être 'projet', 'phase', ou 'operation'
        """
        filter_args = {}
        
        if entity_type == 'projet':
            filter_args['projet_id'] = entity_id
        elif entity_type == 'phase':
            filter_args['phase_id'] = entity_id
        elif entity_type == 'operation':
            filter_args['operation_id'] = entity_id
        else:
            return Response(
                {"error": "Type d'entité invalide. Utilisez 'projet', 'phase', ou 'operation'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        problemes = Probleme.objects.filter(**filter_args).order_by('-date_signalement')
        
        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(problemes, request)
        
        serializer = ProblemeListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SolutionsByProblemeView(APIView):
    """Vue pour récupérer les solutions liées à un problème spécifique"""
    permission_classes = [IsAuthenticated]

    def get(self, request, probleme_id):
        """Récupérer les solutions pour un problème donné"""
        solutions = Solution.objects.filter(probleme_id=probleme_id).order_by('-date_proposition')
        serializer = SolutionListSerializer(solutions, many=True)
        return Response(serializer.data)