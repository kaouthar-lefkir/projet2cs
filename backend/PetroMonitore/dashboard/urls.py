from django.urls import path
from . import views

urlpatterns = [
    # Dashboard général
    path('general/', views.DashboardGeneralView.as_view(), name='dashboard-general'),
    
    # Indicateurs de performance
    path('performance/', views.IndicateurPerformanceGeneralView.as_view(), name='dashboard-performance'),
    
    # Projets par responsable
    path('projets-par-responsable/', views.ProjetParResponsableView.as_view(), name='dashboard-projets-responsable'),
    
    # Indicateurs d'équipe
    path('equipe/', views.IndicateurEquipeView.as_view(), name='dashboard-equipe'),
    
    # Alertes récentes
    path('alertes-recentes/', views.AlertesRecentesView.as_view(), name='dashboard-alertes-recentes'),
    
    # Problèmes récents
    path('problemes-recents/', views.ProblemesRecentsView.as_view(), name='dashboard-problemes-recents'),
    
    # Dashboard spécifique à un projet
    path('projet/<int:projet_id>/', views.ProjetDashboardView.as_view(), name='dashboard-projet'),
    
    # Dashboard spécifique à une phase
    path('phase/<int:phase_id>/', views.PhaseDashboardView.as_view(), name='dashboard-phase'),
    
    # Dashboard spécifique à une opération
    path('operation/<int:operation_id>/', views.OperationDashboardView.as_view(), name='dashboard-operation'),
]