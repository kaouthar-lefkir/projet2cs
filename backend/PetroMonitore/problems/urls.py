from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les problèmes
    path('', views.ProblemeListView.as_view(), name='probleme-list'),
    path('<int:pk>/', views.ProblemeDetailView.as_view(), name='probleme-detail'),
    
    # URLs pour les solutions
    path('solutions/', views.SolutionListView.as_view(), name='solution-list'),
    path('solutions/<int:pk>/', views.SolutionDetailView.as_view(), name='solution-detail'),
    
    # URLs pour les problèmes par entité
    path('entity/<str:entity_type>/<int:entity_id>/', 
         views.ProblemesByEntityView.as_view(), name='problemes-by-entity'),
    
    # URL pour les solutions par problème
    path('<int:probleme_id>/solutions/', 
         views.SolutionsByProblemeView.as_view(), name='solutions-by-probleme'),
    
]