import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from ..models import Utilisateur, Projet, Phase, Operation
from ..serializers import (
    PhaseDetailStatusSerializer,
    ProjetDetailStatusSerializer,
    OperationStatusSerializer
)


class PhaseStatusViewTests(APITestCase):
    """Tests pour PhaseStatusView"""
    
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Test',
            prenom='User',
            role='EXPERT'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet test',
            budget_initial=Decimal('100000.00'),
            cout_actuel=Decimal('50000.00'),
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=180),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            description='Description de la phase test',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=90),
            budget_alloue=Decimal('50000.00'),
            cout_actuel=Decimal('20000.00'),
            progression=Decimal('40.00'),
            statut='EN_COURS'
        )
        
        # Créer des opérations pour la phase
        self.operation1 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 1',
            description='Description opération 1',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30),
            cout_prevue=Decimal('20000.00'),
            cout_reel=Decimal('10000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS',
            responsable=self.user
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 2',
            description='Description opération 2',
            date_debut_prevue=date.today() + timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=60),
            cout_prevue=Decimal('30000.00'),
            cout_reel=Decimal('10000.00'),
            progression=Decimal('30.00'),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Client API avec authentification
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL pour accéder à la vue
        self.url = reverse('phase-status', kwargs={'phase_id': self.phase.id})
    
    def test_get_phase_status(self):
        """Tester l'obtention du statut d'une phase"""
        response = self.client.get(self.url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la réponse contient les informations de statut attendues
        self.assertIn('id', response.data)
        self.assertIn('nom', response.data)
        self.assertIn('progression', response.data)
        self.assertIn('statut_couleur', response.data)
        self.assertIn('operations', response.data)
        
        # Vérifier que les données de la phase sont correctes
        self.assertEqual(response.data['id'], self.phase.id)
        self.assertEqual(response.data['nom'], 'Phase Test')
        
        # Vérifier que les opérations sont incluses
        self.assertEqual(len(response.data['operations']), 2)
    
    def test_phase_status_not_found(self):
        """Tester la réponse quand la phase n'existe pas"""
        url = reverse('phase-status', kwargs={'phase_id': 999})  # ID inexistant
        response = self.client.get(url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier le message d'erreur
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Phase avec ID 999 n\'existe pas')
    
    def test_phase_status_unauthorized(self):
        """Tester l'accès non autorisé"""
        # Client sans authentification
        client = APIClient()
        response = client.get(self.url)
        
        # Vérifier que l'accès est refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjetStatusViewTests(APITestCase):
    """Tests pour ProjetStatusView"""
    
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Test',
            prenom='User',
            role='EXPERT'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet test',
            budget_initial=Decimal('200000.00'),
            cout_actuel=Decimal('100000.00'),
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=365),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Créer des phases pour le projet
        self.phase1 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            description='Description phase 1',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=120),
            budget_alloue=Decimal('80000.00'),
            cout_actuel=Decimal('40000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS'
        )
        
        self.phase2 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            description='Description phase 2',
            ordre=2,
            date_debut_prevue=date.today() + timedelta(days=120),
            date_fin_prevue=date.today() + timedelta(days=240),
            budget_alloue=Decimal('120000.00'),
            cout_actuel=Decimal('60000.00'),
            progression=Decimal('30.00'),
            statut='EN_COURS'
        )
        
        # Créer des opérations pour les phases
        self.operation1 = Operation.objects.create(
            phase=self.phase1,
            nom='Opération 1.1',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=60),
            cout_prevue=Decimal('40000.00'),
            cout_reel=Decimal('20000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS'
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase1,
            nom='Opération 1.2',
            date_debut_prevue=date.today() + timedelta(days=60),
            date_fin_prevue=date.today() + timedelta(days=120),
            cout_prevue=Decimal('40000.00'),
            cout_reel=Decimal('20000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS'
        )
        
        self.operation3 = Operation.objects.create(
            phase=self.phase2,
            nom='Opération 2.1',
            date_debut_prevue=date.today() + timedelta(days=120),
            date_fin_prevue=date.today() + timedelta(days=180),
            cout_prevue=Decimal('60000.00'),
            cout_reel=Decimal('30000.00'),
            progression=Decimal('30.00'),
            statut='EN_COURS'
        )
        
        self.operation4 = Operation.objects.create(
            phase=self.phase2,
            nom='Opération 2.2',
            date_debut_prevue=date.today() + timedelta(days=180),
            date_fin_prevue=date.today() + timedelta(days=240),
            cout_prevue=Decimal('60000.00'),
            cout_reel=Decimal('30000.00'),
            progression=Decimal('30.00'),
            statut='EN_COURS'
        )
        
        # Client API avec authentification
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL pour accéder à la vue
        self.url = reverse('projet-status', kwargs={'projet_id': self.projet.id})
    
    def test_get_projet_status(self):
        """Tester l'obtention du statut d'un projet"""
        response = self.client.get(self.url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la réponse contient les informations de statut attendues
        self.assertIn('id', response.data)
        self.assertIn('nom', response.data)
        self.assertIn('progression', response.data)
        self.assertIn('statut_couleur', response.data)
        self.assertIn('phases', response.data)
        
        # Vérifier que les données du projet sont correctes
        self.assertEqual(response.data['id'], self.projet.id)
        self.assertEqual(response.data['nom'], 'Projet Test')
        
        # Vérifier que les phases sont incluses
        self.assertEqual(len(response.data['phases']), 2)
    
    def test_projet_status_not_found(self):
        """Tester la réponse quand le projet n'existe pas"""
        url = reverse('projet-status', kwargs={'projet_id': 999})  # ID inexistant
        response = self.client.get(url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier le message d'erreur
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Projet avec ID 999 n\'existe pas')
    
    def test_projet_status_unauthorized(self):
        """Tester l'accès non autorisé"""
        # Client sans authentification
        client = APIClient()
        response = client.get(self.url)
        
        # Vérifier que l'accès est refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OperationStatusUpdateViewTests(APITestCase):
    """Tests pour OperationStatusUpdateView"""
    
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Test',
            prenom='User',
            role='EXPERT'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet test',
            budget_initial=Decimal('100000.00'),
            cout_actuel=Decimal('0.00'),
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=180),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            description='Description de la phase test',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=90),
            budget_alloue=Decimal('50000.00'),
            cout_actuel=Decimal('0.00'),
            progression=Decimal('0.00'),
            statut='EN_COURS'
        )
        
        # Créer une opération
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Opération Test',
            description='Description opération test',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30),
            cout_prevue=Decimal('20000.00'),
            cout_reel=Decimal('0.00'),
            progression=Decimal('0.00'),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Client API avec authentification
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL pour accéder à la vue
        self.url = reverse('operation-update-status', kwargs={'operation_id': self.operation.id})
    
    def test_update_operation_status(self):
        """Tester la mise à jour du statut d'une opération"""
        # Données pour la mise à jour
        update_data = {
            'progression': 50.0,
            'cout_reel': 10000.00,
            'date_debut_reelle': date.today().isoformat(),
            'statut': 'EN_COURS'
        }
        
        # Envoyer la requête de mise à jour
        response = self.client.post(self.url, update_data, format='json')
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les données ont été mises à jour
        self.operation.refresh_from_db()
        self.assertEqual(self.operation.progression, Decimal('50.0'))
        self.assertEqual(self.operation.cout_reel, Decimal('10000.00'))
        
        # Vérifier que la phase a également été mise à jour
        self.phase.refresh_from_db()
        self.assertTrue(self.phase.progression > 0)
        self.assertTrue(self.phase.cout_actuel > 0)
        
        # Vérifier que le projet a également été mis à jour
        self.projet.refresh_from_db()
        self.assertTrue(self.projet.cout_actuel > 0)
    
    def test_update_operation_invalid_data(self):
        """Tester la mise à jour avec des données invalides"""
        # Données invalides (progression > 100)
        invalid_data = {
            'progression': 150.0  # Supérieur à 100%
        }
        
        # Envoyer la requête de mise à jour
        response = self.client.post(self.url, invalid_data, format='json')
        
        # Vérifier que la requête est rejetée
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_operation_status_update_not_found(self):
        """Tester la mise à jour pour une opération inexistante"""
        url = reverse('operation-update-status', kwargs={'operation_id': 999})  # ID inexistant
        response = self.client.post(url, {'progression': 50.0}, format='json')
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier le message d'erreur
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Opération avec ID 999 n\'existe pas')
    
    def test_operation_status_update_unauthorized(self):
        """Tester l'accès non autorisé"""
        # Client sans authentification
        client = APIClient()
        response = client.post(self.url, {'progression': 50.0}, format='json')
        
        # Vérifier que l'accès est refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PhaseProgressUpdateViewTests(APITestCase):
    """Tests pour PhaseProgressUpdateView"""
    
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Test',
            prenom='User',
            role='EXPERT'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet test',
            budget_initial=Decimal('100000.00'),
            cout_actuel=Decimal('0.00'),
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=180),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            description='Description de la phase test',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=90),
            budget_alloue=Decimal('50000.00'),
            cout_actuel=Decimal('0.00'),
            progression=Decimal('0.00'),
            statut='EN_COURS'
        )
        
        # Créer des opérations pour la phase
        self.operation1 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 1',
            description='Description opération 1',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30),
            cout_prevue=Decimal('20000.00'),
            cout_reel=Decimal('10000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS'
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 2',
            description='Description opération 2',
            date_debut_prevue=date.today() + timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=60),
            cout_prevue=Decimal('30000.00'),
            cout_reel=Decimal('5000.00'),
            progression=Decimal('25.00'),
            statut='EN_COURS'
        )
        
        # Client API avec authentification
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL pour accéder à la vue
        self.url = reverse('phase-update-progress', kwargs={'phase_id': self.phase.id})
    
    def test_update_phase_progress(self):
        """Tester la mise à jour de la progression d'une phase"""
        # Envoyer la requête de mise à jour
        response = self.client.post(self.url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la progression a été mise à jour
        self.phase.refresh_from_db()
        
        # Selon la logique dans update_phase_progress, la progression devrait être la moyenne pondérée
        # (50% * 20000 + 25% * 30000) / 50000 = 35%
        expected_progression = Decimal('35.00')
        self.assertAlmostEqual(self.phase.progression, expected_progression, delta=0.1)
        
        # Vérifier que les coûts ont été mis à jour
        self.assertAlmostEqual(self.phase.cout_actuel, Decimal('15000.00'))
    
    def test_phase_progress_update_not_found(self):
        """Tester la mise à jour pour une phase inexistante"""
        url = reverse('phase-update-progress', kwargs={'phase_id': 999})  # ID inexistant
        response = self.client.post(url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier le message d'erreur
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Phase avec ID 999 n\'existe pas')
    
    def test_phase_progress_update_unauthorized(self):
        """Tester l'accès non autorisé"""
        # Client sans authentification
        client = APIClient()
        response = client.post(self.url)
        
        # Vérifier que l'accès est refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjetProgressUpdateViewTests(APITestCase):
    """Tests pour ProjetProgressUpdateView"""
    
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Test',
            prenom='User',
            role='EXPERT'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet test',
            budget_initial=Decimal('200000.00'),
            cout_actuel=Decimal('0.00'),
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=365),
            statut='EN_COURS',
            responsable=self.user
        )
        
        # Créer des phases pour le projet
        self.phase1 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            description='Description phase 1',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=120),
            budget_alloue=Decimal('80000.00'),
            cout_actuel=Decimal('30000.00'),
            progression=Decimal('40.00'),
            statut='EN_COURS'
        )
        
        self.phase2 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            description='Description phase 2',
            ordre=2,
            date_debut_prevue=date.today() + timedelta(days=120),
            date_fin_prevue=date.today() + timedelta(days=240),
            budget_alloue=Decimal('120000.00'),
            cout_actuel=Decimal('20000.00'),
            progression=Decimal('20.00'),
            statut='EN_COURS'
        )
        
        # Créer des opérations pour les phases
        self.operation1 = Operation.objects.create(
            phase=self.phase1,
            nom='Opération 1.1',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=60),
            cout_prevue=Decimal('40000.00'),
            cout_reel=Decimal('20000.00'),
            progression=Decimal('50.00'),
            statut='EN_COURS'
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase1,
            nom='Opération 1.2',
            date_debut_prevue=date.today() + timedelta(days=60),
            date_fin_prevue=date.today() + timedelta(days=120),
            cout_prevue=Decimal('40000.00'),
            cout_reel=Decimal('10000.00'),
            progression=Decimal('30.00'),
            statut='EN_COURS'
        )
        
        self.operation3 = Operation.objects.create(
            phase=self.phase2,
            nom='Opération 2.1',
            date_debut_prevue=date.today() + timedelta(days=120),
            date_fin_prevue=date.today() + timedelta(days=180),
            cout_prevue=Decimal('60000.00'),
            cout_reel=Decimal('15000.00'),
            progression=Decimal('25.00'),
            statut='EN_COURS'
        )
        
        self.operation4 = Operation.objects.create(
            phase=self.phase2,
            nom='Opération 2.2',
            date_debut_prevue=date.today() + timedelta(days=180),
            date_fin_prevue=date.today() + timedelta(days=240),
            cout_prevue=Decimal('60000.00'),
            cout_reel=Decimal('5000.00'),
            progression=Decimal('15.00'),
            statut='EN_COURS'
        )
        
        # Client API avec authentification
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL pour accéder à la vue
        self.url = reverse('projet-update-progress', kwargs={'projet_id': self.projet.id})
    
    def test_update_projet_progress(self):
        """Tester la mise à jour de la progression et des coûts d'un projet"""
        # Envoyer la requête de mise à jour
        response = self.client.post(self.url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les coûts ont été mis à jour
        self.projet.refresh_from_db()
        self.assertEqual(self.projet.cout_actuel, Decimal('50000.00'))  # 30000 + 20000
        
        # Vérifier que les phases ont été mises à jour
        self.phase1.refresh_from_db()
        self.phase2.refresh_from_db()
        
        # Les phases devraient avoir été mises à jour avec les bonnes progressions
        # et les bons coûts en fonction des opérations
        self.assertAlmostEqual(self.phase1.cout_actuel, Decimal('30000.00'))
        self.assertAlmostEqual(self.phase2.cout_actuel, Decimal('20000.00'))
        
        # Vérifier que les données dans la réponse sont correctes
        self.assertIn('id', response.data)
        self.assertIn('nom', response.data)
        self.assertIn('cout_actuel', response.data)
        self.assertIn('progression', response.data)
        self.assertIn('statut_couleur', response.data)
        self.assertIn('phases', response.data)
        
        # Vérifier les valeurs importantes
        self.assertEqual(response.data['id'], self.projet.id)
        self.assertEqual(len(response.data['phases']), 2)
    
    def test_projet_progress_update_not_found(self):
        """Tester la mise à jour pour un projet inexistant"""
        url = reverse('projet-update-progress', kwargs={'projet_id': 999})  # ID inexistant
        response = self.client.post(url)
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier le message d'erreur
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Projet avec ID 999 n\'existe pas')
    
    def test_projet_progress_update_unauthorized(self):
        """Tester l'accès non autorisé"""
        # Client sans authentification
        client = APIClient()
        response = client.post(self.url)
        
        # Vérifier que l'accès est refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)