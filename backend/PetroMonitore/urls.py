from django.urls import path, include
from .views import (
    EquipeProjetDetail,
    EquipeProjetListCreate,
    HistoriqueSeuilDetailView,
    HistoriqueSeuilListView,
    LoginView,
    OperationDetailView,
    OperationListView,
    OperationOrderingView,
    OperationProgressionView,
    OperationStatusUpdateView,
    PhaseDetailView,
    PhaseListView,
    PhaseOrderingView,
    PhaseProgressUpdateView,
    PhaseStatusView,
    ProjetDetailView,
    ProjetListView,
    ProjetProgressUpdateView,
    ProjetResponsableView,
    ProjetStatusView,
    ProjetStatutView,
    SeuilDetailView,
    SeuilHistoriqueView,
    SeuilInitialiserOperationView,
    SeuilListCreateView,
    SeuilOperationView,
    UserListView,
    UserDetailView,
    ChangePasswordView,
    ProfileView,
    LogoutView,
    affecter_utilisateur,
    desaffecter_utilisateur,
    projet_membres,
)

urlpatterns = [
    #login and user management
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),  
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    
    
    #URLs pour la gestion des projets
    path('projets/', ProjetListView.as_view(), name='projet-list'),
    path('projets/<int:pk>/', ProjetDetailView.as_view(), name='projet-detail'),
    path('projets/<int:pk>/statut/', ProjetStatutView.as_view(), name='projet-statut'),
    path('projets/<int:pk>/responsable/', ProjetResponsableView.as_view(), name='projet-responsable'),
    
    
    # Routes pour les phases
    path('projets/<int:projet_id>/phases/', PhaseListView.as_view(), name='phase-list'),
    path('phases/<int:pk>/', PhaseDetailView.as_view(), name='phase-detail'),
    path('projets/<int:projet_id>/phases/order/', PhaseOrderingView.as_view(), name='phase-ordering'),
    
    # Routes pour les opérations
    path('phases/<int:phase_id>/operations/', OperationListView.as_view(), name='operation-list'),
    path('operations/<int:pk>/', OperationDetailView.as_view(), name='operation-detail'),
    path('phases/<int:phase_id>/operations/order/', OperationOrderingView.as_view(), name='operation-ordering'),
    path('operations/<int:pk>/progression/', OperationProgressionView.as_view(), name='operation-progression'),
    
    # Endpoints pour la gestion des équipes
    path('', EquipeProjetListCreate.as_view(), name='equipe-list-create'),
    path('<int:pk>/', EquipeProjetDetail.as_view(), name='equipe-detail'),
    path('projet/<int:projet_id>/membres/', projet_membres, name='projet-membres'),
    path('affecter/', affecter_utilisateur, name='affecter-utilisateur'),
    path('desaffecter/<int:equipe_id>/', desaffecter_utilisateur, name='desaffecter-utilisateur'),
    
    
    # URLs pour les seuils - vues basées sur des classes
    path('seuils/', SeuilListCreateView.as_view(), name='seuil-list'),
    path('seuils/<int:pk>/', SeuilDetailView.as_view(), name='seuil-detail'),
    path('seuils/<int:pk>/historique/', SeuilHistoriqueView.as_view(), name='seuil-historique'),
    path('operations/<int:operation_id>/seuils/', SeuilOperationView.as_view(), name='seuil-operation'),
    path('operations/seuils/initialiser/', SeuilInitialiserOperationView.as_view(), name='seuil-initialiser-operation'),
    
    # URLs pour l'historique des seuils - vues basées sur des classes
    path('historique-seuils/', HistoriqueSeuilListView.as_view(), name='historique-seuil-list'),
    path('historique-seuils/<int:pk>/', HistoriqueSeuilDetailView.as_view(), name='historique-seuil-detail'),
    
    # URLs pour les opérations de statut et de progression - vues basées sur des classes
    path('phases/<int:phase_id>/status/', PhaseStatusView.as_view(), name='phase-status'),
    path('projets/<int:projet_id>/status/', ProjetStatusView.as_view(), name='projet-status'),
    path('operations/<int:operation_id>/update-status/', OperationStatusUpdateView.as_view(), name='operation-update-status'),
    path('phases/<int:phase_id>/update-progress/', PhaseProgressUpdateView.as_view(), name='phase-update-progress'),
    path('projets/<int:projet_id>/update-progress/', ProjetProgressUpdateView.as_view(), name='projet-update-progress'),
    
    #dashboard urls 
    path('dashboard/', include('PetroMonitore.dashboard.urls')),
    
    #url pour la gestion des problèmes
    path('problems/', include('PetroMonitore.problems.urls')), 
    
    
    # URLs spécifiques aux solutions
    path('solutions/', include('PetroMonitore.problems.solution_urls')),
    
    
    #URLS pour la gestion des alertes
    path('alerts/', include('PetroMonitore.alerts.urls')),


]