from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
import json

from ..models import (
    Utilisateur, Projet, Phase, Operation, Probleme, 
    EquipeProjet, Alerte, Solution
)
from .serializers import (
    DashboardGeneralSerializer, ResponsableProjectCountSerializer,
    ProjetDashboardSerializer, PhaseDashboardSerializer, OperationDashboardSerializer,
    IndicateursPerformanceSerializer, IndicateursEquipeSerializer, StatistiquesEquipeProjetSerializer
)


class SerializerTestCase(TestCase):
    """Tests pour les sérialiseurs"""
    
    def setUp(self):
        """Initialiser les données de test communes"""
        # Créer un utilisateur pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            role="INGENIEUR_TERRAIN"
        )
        self.utilisateur.set_password("password123")
        self.utilisateur.save()
        
        # Créer un projet pour les tests
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            budget_initial=100000.00,
            cout_actuel=50000.00,
            date_debut=date.today() - timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=60),
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        # Créer une phase pour les tests
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            description="Description de la phase test",
            ordre=1,
            date_debut_prevue=date.today() - timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=30),
            date_debut_reelle=date.today() - timedelta(days=25),
            budget_alloue=50000.00,
            cout_actuel=25000.00,
            progression=50.0,
            statut="EN_COURS"
        )
        
        # Créer une opération pour les tests
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Opération Test",
            description="Description de l'opération test",
            date_debut_prevue=date.today() - timedelta(days=20),
            date_fin_prevue=date.today() + timedelta(days=10),
            date_debut_reelle=date.today() - timedelta(days=18),
            cout_prevue=20000.00,
            cout_reel=10000.00,
            progression=50.0,
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        # Créer un problème pour les tests
        self.probleme = Probleme.objects.create(
            projet=self.projet,
            phase=self.phase,
            operation=self.operation,
            titre="Problème Test",
            description="Description du problème test",
            gravite="MOYENNE",
            statut="OUVERT",
            signale_par=self.utilisateur
        )
        
        # Créer une équipe pour les tests
        self.equipe_projet = EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.utilisateur,
            role_projet="Chef de projet",
            affecte_par=self.utilisateur
        )
        
        # Créer une alerte pour les tests
        self.alerte = Alerte.objects.create(
            projet=self.projet,
            phase=self.phase,
            operation=self.operation,
            type_alerte="Retard",
            niveau="WARNING",
            message="Alerte de test",
            statut="NON_LU"
        )
    
    def test_dashboard_general_serializer(self):
        """Test pour le sérialiseur DashboardGeneralSerializer"""
        data = {
            'total_projets': 10,
            'projets_planifies': 2,
            'projets_en_cours': 5,
            'projets_termines': 2,
            'projets_suspendus': 1,
            'budget_initial_total': Decimal('1000000.00'),
            'cout_actuel_total': Decimal('750000.00'),
            'ecart_budgetaire': Decimal('-250000.00'),
            'projets_en_retard': 2,
            'retard_moyen_jours': 15.5,
            'progression_moyenne': 65.0,
            'taux_reussite': 75.0
        }
        
        serializer = DashboardGeneralSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['total_projets'], 10)
        self.assertEqual(serializer.data['projets_en_cours'], 5)
        self.assertEqual(serializer.data['budget_initial_total'], '1000000.00')
        self.assertEqual(serializer.data['cout_actuel_total'], '750000.00')
        self.assertEqual(serializer.data['ecart_budgetaire'], '-250000.00')
        self.assertEqual(serializer.data['retard_moyen_jours'], 15.5)
        self.assertEqual(serializer.data['progression_moyenne'], 65.0)
    
    def test_responsable_project_count_serializer(self):
        """Test pour le sérialiseur ResponsableProjectCountSerializer"""
        data = {
            'responsable_id': self.utilisateur.id,
            'responsable_nom': f"{self.utilisateur.prenom} {self.utilisateur.nom}",
            'nombre_projets': 3
        }
        
        serializer = ResponsableProjectCountSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['responsable_id'], self.utilisateur.id)
        self.assertEqual(serializer.data['responsable_nom'], "Jean Dupont")
        self.assertEqual(serializer.data['nombre_projets'], 3)
    
    def test_projet_dashboard_serializer(self):
        """Test pour le sérialiseur ProjetDashboardSerializer"""
        data = {
            'id': self.projet.id,
            'nom': self.projet.nom,
            'progression': 45.0,
            'statut_cout': 'VERT',
            'statut_delai': 'JAUNE',
            'statut_global': 'JAUNE',
            'budget_initial': Decimal('100000.00'),
            'cout_actuel': Decimal('50000.00'),
            'pourcentage_budget_consomme': 50.0,
            'date_debut': self.projet.date_debut,
            'date_fin_prevue': self.projet.date_fin_prevue,
            'date_fin_reelle': None,
            'retard_jours': 0,
            'retard_pourcentage': 0.0,
            'alertes_critiques': 1,
            'alertes_avertissements': 2,
            'alertes_informations': 3,
            'problemes_non_resolus_critiques': 0,
            'problemes_non_resolus_eleves': 1,
            'problemes_non_resolus_moyens': 2,
            'problemes_non_resolus_faibles': 1
        }
        
        serializer = ProjetDashboardSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['nom'], self.projet.nom)
        self.assertEqual(serializer.data['progression'], 45.0)
        self.assertEqual(serializer.data['statut_cout'], 'VERT')
        self.assertEqual(serializer.data['statut_delai'], 'JAUNE')
        self.assertEqual(serializer.data['statut_global'], 'JAUNE')
        self.assertEqual(serializer.data['budget_initial'], '100000.00')
        self.assertEqual(serializer.data['retard_jours'], 0)
    
    def test_phase_dashboard_serializer(self):
        """Test pour le sérialiseur PhaseDashboardSerializer"""
        data = {
            'id': self.phase.id,
            'nom': self.phase.nom,
            'progression': 50.0,
            'statut_cout': 'VERT',
            'statut_delai': 'VERT',
            'statut_global': 'VERT',
            'budget_alloue': Decimal('50000.00'),
            'cout_actuel': Decimal('25000.00'),
            'pourcentage_budget_consomme': 50.0,
            'date_debut_prevue': self.phase.date_debut_prevue,
            'date_fin_prevue': self.phase.date_fin_prevue,
            'date_debut_reelle': self.phase.date_debut_reelle,
            'date_fin_reelle': None,
            'retard_jours': 0,
            'operations_terminees': 2,
            'operations_en_cours': 3,
            'operations_planifiees': 1,
            'operations_suspendues': 0,
            'pourcentage_operations_retard': 10.0
        }
        
        serializer = PhaseDashboardSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['nom'], self.phase.nom)
        self.assertEqual(serializer.data['progression'], 50.0)
        self.assertEqual(serializer.data['statut_cout'], 'VERT')
        self.assertEqual(serializer.data['statut_delai'], 'VERT')
        self.assertEqual(serializer.data['statut_global'], 'VERT')
        self.assertEqual(serializer.data['budget_alloue'], '50000.00')
        self.assertEqual(serializer.data['operations_terminees'], 2)
        self.assertEqual(serializer.data['operations_en_cours'], 3)
    
    def test_operation_dashboard_serializer(self):
        """Test pour le sérialiseur OperationDashboardSerializer"""
        data = {
            'id': self.operation.id,
            'nom': self.operation.nom,
            'progression': 50.0,
            'statut_cout': 'VERT',
            'statut_delai': 'VERT',
            'statut_global': 'VERT',
            'cout_prevue': Decimal('20000.00'),
            'cout_reel': Decimal('10000.00'),
            'ecart_cout': Decimal('-10000.00'),
            'pourcentage_ecart_cout': -50.0,
            'date_debut_prevue': self.operation.date_debut_prevue,
            'date_fin_prevue': self.operation.date_fin_prevue,
            'date_debut_reelle': self.operation.date_debut_reelle,
            'date_fin_reelle': None,
            'retard_jours': 0,
            'problemes_ouverts': 1,
            'problemes_en_cours': 0,
            'problemes_resolus': 0
        }
        
        serializer = OperationDashboardSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['nom'], self.operation.nom)
        self.assertEqual(serializer.data['progression'], 50.0)
        self.assertEqual(serializer.data['statut_cout'], 'VERT')
        self.assertEqual(serializer.data['statut_delai'], 'VERT')
        self.assertEqual(serializer.data['statut_global'], 'VERT')
        self.assertEqual(serializer.data['cout_prevue'], '20000.00')
        self.assertEqual(serializer.data['cout_reel'], '10000.00')
        self.assertEqual(serializer.data['ecart_cout'], '-10000.00')
    
    def test_indicateurs_performance_serializer(self):
        """Test pour le sérialiseur IndicateursPerformanceSerializer"""
        data = {
            'efficacite': 1.2,
            'productivite_cout': Decimal('0.05'),
            'productivite_temps': 0.8,
            'qualite_problemes': 1.5,
            'temps_resolution_moyen': 3.2
        }
        
        serializer = IndicateursPerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['efficacite'], 1.2)
        self.assertEqual(serializer.data['productivite_cout'], '0.05')
        self.assertEqual(serializer.data['productivite_temps'], 0.8)
        self.assertEqual(serializer.data['qualite_problemes'], 1.5)
        self.assertEqual(serializer.data['temps_resolution_moyen'], 3.2)
    
    def test_indicateurs_equipe_serializer(self):
        """Test pour le sérialiseur IndicateursEquipeSerializer"""
        # Test with model instance
        serializer = IndicateursEquipeSerializer(self.equipe_projet)
        self.assertEqual(serializer.data['id'], self.utilisateur.id)
        self.assertEqual(serializer.data['nom_complet'], f"{self.utilisateur.prenom} {self.utilisateur.nom}")
        self.assertEqual(serializer.data['role_projet'], 'Chef de projet')
        
        # Test with dictionary - provide the data in the expected format
        equipe_data = {
            'id': self.utilisateur.id,
            'nom_complet': f"{self.utilisateur.prenom} {self.utilisateur.nom}",
            'role_projet': 'Chef de projet',
            'operations_assignees': 5,
            'progression_moyenne': 65.0
        }
        serializer = IndicateursEquipeSerializer(equipe_data)
        self.assertEqual(serializer.data['id'], self.utilisateur.id)
        self.assertEqual(serializer.data['role_projet'], 'Chef de projet')
    
    def test_statistiques_equipe_projet_serializer(self):
        """Test pour le sérialiseur StatistiquesEquipeProjetSerializer"""
        data = {
            'nombre_membres': 10,
            'ingenieur_terrain': 6,
            'expert': 3,
            'top_management': 1
        }
        
        serializer = StatistiquesEquipeProjetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['nombre_membres'], 10)
        self.assertEqual(serializer.data['ingenieur_terrain'], 6)
        self.assertEqual(serializer.data['expert'], 3)
        self.assertEqual(serializer.data['top_management'], 1)


class ViewsTestCase(APITestCase):
    """Tests pour les vues API"""
    
    def setUp(self):
        """Initialiser les données de test communes"""
        # Créer un utilisateur pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            role="INGENIEUR_TERRAIN",
            is_staff=True,
            is_superuser=True
        )
        self.utilisateur.set_password("password123")
        self.utilisateur.save()
        
        # Authentifier le client
        self.client = APIClient()
        self.client.force_authenticate(user=self.utilisateur)
        
        # Créer un projet pour les tests
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            budget_initial=100000.00,
            cout_actuel=50000.00,
            date_debut=date.today() - timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=60),
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        # Créer une phase pour les tests
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            description="Description de la phase test",
            ordre=1,
            date_debut_prevue=date.today() - timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=30),
            date_debut_reelle=date.today() - timedelta(days=25),
            budget_alloue=50000.00,
            cout_actuel=25000.00,
            progression=50.0,
            statut="EN_COURS"
        )
        
        # Créer une opération pour les tests
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Opération Test",
            description="Description de l'opération test",
            date_debut_prevue=date.today() - timedelta(days=20),
            date_fin_prevue=date.today() + timedelta(days=10),
            date_debut_reelle=date.today() - timedelta(days=18),
            cout_prevue=20000.00,
            cout_reel=10000.00,
            progression=50.0,
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        # Créer un problème pour les tests
        self.probleme = Probleme.objects.create(
            projet=self.projet,
            phase=self.phase,
            operation=self.operation,
            titre="Problème Test",
            description="Description du problème test",
            gravite="MOYENNE",
            statut="OUVERT",
            signale_par=self.utilisateur
        )
        
        # Créer une équipe pour les tests
        self.equipe_projet = EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.utilisateur,
            role_projet="Chef de projet",
            affecte_par=self.utilisateur
        )
        
        # Créer une alerte pour les tests
        self.alerte = Alerte.objects.create(
            projet=self.projet,
            phase=self.phase,
            operation=self.operation,
            type_alerte="Retard",
            niveau="WARNING",
            message="Alerte de test",
            statut="NON_LU"
        )
    
    def test_dashboard_general_view(self):
        """Test pour la vue DashboardGeneralView"""
        url = reverse('dashboard-general')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_projets', response.data)
        self.assertIn('projets_en_cours', response.data)
        self.assertIn('budget_initial_total', response.data)
        self.assertIn('cout_actuel_total', response.data)
        self.assertIn('ecart_budgetaire', response.data)
        self.assertIn('progression_moyenne', response.data)
        self.assertIn('taux_reussite', response.data)
        
        # Vérifier que le total des projets est correct
        self.assertEqual(response.data['total_projets'], Projet.objects.count())
    
    def test_indicateur_performance_general_view(self):
        """Test pour la vue IndicateurPerformanceGeneralView"""
        url = reverse('dashboard-performance')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('efficacite', response.data)
        self.assertIn('productivite_cout', response.data)
        self.assertIn('productivite_temps', response.data)
        self.assertIn('qualite_problemes', response.data)
        self.assertIn('temps_resolution_moyen', response.data)
    
    def test_projet_par_responsable_view(self):
        """Test pour la vue ProjetParResponsableView"""
        url = reverse('dashboard-projets-responsable')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        
        # Si l'utilisateur a au moins un projet
        if Projet.objects.filter(responsable=self.utilisateur).exists():
            self.assertTrue(len(response.data) > 0)
            self.assertIn('responsable_id', response.data[0])
            self.assertIn('responsable_nom', response.data[0])
            self.assertIn('nombre_projets', response.data[0])
    
    def test_indicateur_equipe_view_with_projet_id(self):
        """Test pour la vue IndicateurEquipeView avec un ID de projet"""
        url = reverse('dashboard-equipe')
        response = self.client.get(f"{url}?projet_id={self.projet.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistiques_generales', response.data)
        self.assertIn('indicateurs_membres', response.data)
        
        # Vérifier les statistiques générales
        self.assertIn('nombre_membres', response.data['statistiques_generales'])
        self.assertIn('ingenieur_terrain', response.data['statistiques_generales'])
        self.assertIn('expert', response.data['statistiques_generales'])
        self.assertIn('top_management', response.data['statistiques_generales'])
    
    def test_indicateur_equipe_view_without_projet_id(self):
        """Test pour la vue IndicateurEquipeView sans ID de projet"""
        url = reverse('dashboard-equipe')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Un ID de projet est requis pour cette vue")
    
    def test_alertes_recentes_view(self):
        """Test pour la vue AlertesRecentesView"""
        url = reverse('dashboard-alertes-recentes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        
        # S'il y a des alertes
        if Alerte.objects.exists():
            self.assertTrue(len(response.data) > 0)
            self.assertIn('id', response.data[0])
            self.assertIn('type', response.data[0])
            self.assertIn('niveau', response.data[0])
            self.assertIn('message', response.data[0])
            self.assertIn('statut', response.data[0])
            self.assertIn('contexte', response.data[0])
    
    def test_problemes_recents_view(self):
        """Test pour la vue ProblemesRecentsView"""
        url = reverse('dashboard-problemes-recents')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        
        # S'il y a des problèmes
        if Probleme.objects.exists():
            self.assertTrue(len(response.data) > 0)
            self.assertIn('id', response.data[0])
            self.assertIn('titre', response.data[0])
            self.assertIn('description', response.data[0])
            self.assertIn('gravite', response.data[0])
            self.assertIn('statut', response.data[0])
            self.assertIn('contexte', response.data[0])
            self.assertIn('nb_solutions', response.data[0])
    
    def test_projet_dashboard_view(self):
        """Test pour la vue ProjetDashboardView"""
        url = reverse('dashboard-projet', args=[self.projet.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.projet.id)
        self.assertEqual(response.data['nom'], self.projet.nom)
        self.assertIn('progression', response.data)
        self.assertIn('statut_cout', response.data)
        self.assertIn('statut_delai', response.data)
        self.assertIn('statut_global', response.data)
        self.assertIn('budget_initial', response.data)
        self.assertIn('cout_actuel', response.data)
        self.assertIn('date_debut', response.data)
        self.assertIn('date_fin_prevue', response.data)
    
    def test_projet_dashboard_view_invalid_id(self):
        """Test pour la vue ProjetDashboardView avec un ID invalide"""
        url = reverse('dashboard-projet', args=[9999])  # ID inexistant
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_phase_dashboard_view(self):
        """Test pour la vue PhaseDashboardView"""
        # Ensure phase has the expected progression
        self.phase.progression = 50.0
        self.phase.save()
        
        url = reverse('dashboard-phase', args=[self.phase.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['progression']), float(self.phase.progression))
    
    def test_phase_dashboard_view_invalid_id(self):
        """Test pour la vue PhaseDashboardView avec un ID invalide"""
        url = reverse('dashboard-phase', args=[9999])  # ID inexistant
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_operation_dashboard_view(self):
        """Test pour la vue OperationDashboardView"""
        url = reverse('dashboard-operation', args=[self.operation.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.operation.id)
        self.assertEqual(response.data['nom'], self.operation.nom)
        self.assertEqual(response.data['progression'], float(self.operation.progression))
        self.assertIn('statut_cout', response.data)
        self.assertIn('statut_delai', response.data)
        self.assertIn('statut_global', response.data)
        self.assertIn('cout_prevue', response.data)
        self.assertIn('cout_reel', response.data)
        self.assertIn('ecart_cout', response.data)
        self.assertIn('problemes_ouverts', response.data)
        self.assertIn('problemes_en_cours', response.data)
        self.assertIn('problemes_resolus', response.data)
    
    def test_operation_dashboard_view_invalid_id(self):
        """Test pour la vue OperationDashboardView avec un ID invalide"""
        url = reverse('dashboard-operation', args=[9999])  # ID inexistant
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)