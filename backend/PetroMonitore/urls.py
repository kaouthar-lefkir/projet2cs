from django.urls import path
from .views import (
    EquipeProjetDetail,
    EquipeProjetListCreate,
    LoginView,
    OperationDetailView,
    OperationListView,
    OperationOrderingView,
    OperationProgressionView,
    PhaseDetailView,
    PhaseListView,
    PhaseOrderingView,
    ProjetDetailView,
    ProjetListView,
    ProjetResponsableView,
    ProjetStatutView,
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
]