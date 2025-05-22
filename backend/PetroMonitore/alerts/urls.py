# PteroMonitore/alerts/urls.py
from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # CRUD des alertes
    path('', views.AlerteListCreateView.as_view(), name='alerte-list-create'),
    path('<int:pk>/', views.AlerteDetailView.as_view(), name='alerte-detail'),
    
    # Actions sur les alertes
    path('<int:pk>/marquer-lue/', views.marquer_alerte_lue, name='marquer-alerte-lue'),
    path('<int:pk>/marquer-traitee/', views.marquer_alerte_traitee, name='marquer-alerte-traitee'),
    path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer-toutes-lues'),
    
    # Statistiques et rapports
    path('statistiques/', views.statistiques_alertes, name='statistiques-alertes'),
    path('historique/', views.historique_alertes, name='historique-alertes'),
    path('tableau-bord/', views.alertes_tableau_bord, name='alertes-tableau-bord'),
    
    # Détection automatique
    path('detecter-automatiques/', views.detecter_alertes_automatiques, name='detecter-alertes-automatiques'),
]