from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models import Solution, Projet, Probleme
from .serializers import SolutionListSerializer
from .solution_utils import get_solution_statistics, get_solutions_to_implement


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SolutionStatisticsView(APIView):
    """Vue pour obtenir des statistiques sur les solutions"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtenir des statistiques sur les solutions avec filtres optionnels"""
        probleme_id = request.query_params.get('probleme')
        projet_id = request.query_params.get('projet')
        
        statistics = get_solution_statistics(probleme_id, projet_id)
        return Response(statistics)


class SolutionsAdvancedFilterView(APIView):
    """Vue pour filtrer les solutions de manière avancée"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Filtrer les solutions selon plusieurs critères"""
        solutions = Solution.objects.all().order_by('-date_proposition')
        
        # Filtres de base
        probleme_id = request.query_params.get('probleme')
        if probleme_id:
            solutions = solutions.filter(probleme_id=probleme_id)
            
        statut = request.query_params.get('statut')
        if statut:
            solutions = solutions.filter(statut=statut)
        
        # Filtres avancés
        type_solution = request.query_params.get('type')
        if type_solution:
            solutions = solutions.filter(type_solution__icontains=type_solution)
            
        # Filtres pour coût estimé
        cout_min = request.query_params.get('cout_min')
        if cout_min:
            solutions = solutions.filter(cout_estime__gte=float(cout_min))
            
        cout_max = request.query_params.get('cout_max')
        if cout_max:
            solutions = solutions.filter(cout_estime__lte=float(cout_max))
            
        # Filtres pour délai estimé
        delai_min = request.query_params.get('delai_min')
        if delai_min:
            solutions = solutions.filter(delai_estime__gte=int(delai_min))
            
        delai_max = request.query_params.get('delai_max')
        if delai_max:
            solutions = solutions.filter(delai_estime__lte=int(delai_max))
        
        # Recherche textuelle
        search = request.query_params.get('search')
        if search:
            solutions = solutions.filter(
                Q(description__icontains=search) |
                Q(probleme__titre__icontains=search)
            )
            
        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(solutions, request)
        
        serializer = SolutionListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SolutionsToImplementView(APIView):
    """Vue pour obtenir les solutions validées mais non encore mises en œuvre"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """Récupérer les solutions validées à mettre en œuvre"""
        projet_id = request.query_params.get('projet')
        solutions = get_solutions_to_implement(projet_id)
        
        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(solutions, request)
        
        serializer = SolutionListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class SolutionsMiseEnOeuvreView(APIView):
    """Vue pour marquer une solution comme mise en œuvre"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """Marquer une solution comme mise en œuvre"""
        solution = get_object_or_404(Solution, pk=pk)
        old_status = solution.statut
        
        # Vérifier que la solution est validée
        if solution.statut != 'VALIDEE':
            return Response(
                {"error": "Seules les solutions validées peuvent être mises en œuvre"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le statut
        solution.statut = 'MISE_EN_OEUVRE'
        solution.save()
        
        # Enregistrer le changement dans l'historique
        from .utils import track_solution_status_change
        track_solution_status_change(solution.id, old_status, 'MISE_EN_OEUVRE', request.user)
        
        return Response(SolutionListSerializer(solution).data)


class SolutionsByProjetView(APIView):
    """Vue pour récupérer les solutions liées à un projet"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, projet_id):
        """Récupérer les solutions pour un projet donné"""
        # Vérifier que le projet existe
        projet = get_object_or_404(Projet, pk=projet_id)
        
        # Récupérer tous les problèmes liés au projet
        problemes = Probleme.objects.filter(projet=projet)
        
        # Récupérer toutes les solutions liées à ces problèmes
        solutions = Solution.objects.filter(probleme__in=problemes).order_by('-date_proposition')
        
        # Appliquer des filtres si présents
        statut = request.query_params.get('statut')
        if statut:
            solutions = solutions.filter(statut=statut)
        
        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(solutions, request)
        
        serializer = SolutionListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)