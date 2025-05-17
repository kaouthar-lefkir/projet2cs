from django.urls import path
from . import solution_views

urlpatterns = [
    # URLs pour les statistiques et filtres avancés des solutions
    path('statistics/', solution_views.SolutionStatisticsView.as_view(), name='solution-statistics'),
    path('advanced-filter/', solution_views.SolutionsAdvancedFilterView.as_view(), name='solution-advanced-filter'),
    
    # URLs pour la gestion de la mise en œuvre des solutions
    path('to-implement/', solution_views.SolutionsToImplementView.as_view(), name='solutions-to-implement'),
    path('<int:pk>/implement/', solution_views.SolutionsMiseEnOeuvreView.as_view(), name='solution-implement'),
    
    # URL pour les solutions par projet
    path('by-projet/<int:projet_id>/', solution_views.SolutionsByProjetView.as_view(), name='solutions-by-projet'),
]