from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from ..models import Projet, Phase, Operation, Alerte, Seuil
from .utils import verifier_seuils_projet, verifier_seuils_operation, creer_alerte

User = get_user_model()


class AlerteModelTest(TestCase):
    """Tests pour le modèle Alerte"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test1@example.com',
            password='testpass123',
            nom='Testt',
            prenom='User',
            role='EXPERT'
        )
        
        self.projet = Projet.objects.create(
            nom='Projet Test',
            statut='EN_COURS',
            budget_initial=Decimal('100000.00'),
            cout_actuel=Decimal('85000.00'),
            seuil_alerte_cout=Decimal('80.00'),
            responsable=self.user
        )
    
    def test_creation_alerte(self):
        """Test de création d'une alerte"""
        alerte = Alerte.objects.create(
            projet=self.projet,
            type_alerte='DEPASSEMENT_BUDGET',
            niveau='WARNING',
            message='Test alerte'
        )
        
        self.assertEqual(alerte.statut, 'NON_LU')
        self.assertIsNotNone(alerte.date_alerte)
        self.assertEqual(str(alerte), 'DEPASSEMENT_BUDGET - Projet Test')
    
    def test_alerte_str_representation(self):
        """Test de la représentation string d'une alerte"""
        alerte = Alerte.objects.create(
            projet=self.projet,
            type_alerte='TEST',
            niveau='INFO',
            message='Test message'
        )
        
        expected_str = 'TEST - Projet Test'
        self.assertEqual(str(alerte), expected_str)


class AlerteUtilsTest(TestCase):
    """Tests pour les utilitaires d'alertes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test1@example.com',
            password='testpass123',
            nom='Testt',
            prenom='User',
            role='EXPERT'
        )
        
        self.projet = Projet.objects.create(
            nom='Projet Test',
            statut='EN_COURS',
            budget_initial=Decimal('100000.00'),
            cout_actuel=Decimal('85000.00'),
            seuil_alerte_cout=Decimal('80.00'),
            responsable=self.user,
            date_debut=date.today() - timedelta(days=30),
            date_fin_prevue=date.today() + timedelta(days=10)
        )
        
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            statut='EN_COURS',
            ordre=1,
            progression=Decimal('50.00')
        )
        
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Operation Test',
            statut='EN_COURS',
            cout_reel=Decimal('15000.00'),
            responsable=self.user
        )
        
        self.seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('10000.00'),
            valeur_jaune=Decimal('12000.00'),
            valeur_rouge=Decimal('18000.00'),
            defini_par=self.user
        )
    
    def test_creer_alerte(self):
        """Test de création d'alerte via utilitaire"""
        alerte = creer_alerte(
            'TEST_ALERTE',
            'INFO',
            'Message de test',
            projet=self.projet
        )
        
        self.assertIsNotNone(alerte)
        self.assertEqual(alerte.type_alerte, 'TEST_ALERTE')
        self.assertEqual(alerte.niveau, 'INFO')
        self.assertEqual(alerte.projet, self.projet)
    
    def test_verifier_seuils_projet_budget(self):
        """Test de vérification des seuils de budget"""
        # Le projet a un coût de 85000€ pour un budget de 100000€ avec seuil à 80%
        # Cela devrait déclencher une alerte
        alertes = verifier_seuils_projet(self.projet)
        
        self.assertTrue(len(alertes) > 0)
        alerte_budget = next((a for a in alertes if a.type_alerte == 'DEPASSEMENT_BUDGET'), None)
        self.assertIsNotNone(alerte_budget)
        self.assertEqual(alerte_budget.niveau, 'WARNING')
    
    def test_verifier_seuils_projet_delai(self):
        """Test de vérification des seuils de délai"""
        # Modifier le projet pour qu'il soit en retard
        self.projet.date_fin_prevue = date.today() - timedelta(days=5)
        self.projet.save()
        
        alertes = verifier_seuils_projet(self.projet)
        
        alerte_delai = next((a for a in alertes if a.type_alerte == 'DEPASSEMENT_DELAI'), None)
        self.assertIsNotNone(alerte_delai)
        self.assertEqual(alerte_delai.niveau, 'CRITIQUE')
    
    def test_verifier_seuils_operation(self):
        """Test de vérification des seuils d'opération"""
        # L'opération coûte 15000€, le seuil jaune est à 12000€
        alertes = verifier_seuils_operation(self.operation)
        
        self.assertTrue(len(alertes) > 0)
        alerte_seuil = alertes[0]
        self.assertEqual(alerte_seuil.type_alerte, 'DEPASSEMENT_SEUIL')
        self.assertEqual(alerte_seuil.niveau, 'WARNING')


class AlerteAPITest(APITestCase):
    """Tests pour l'API des alertes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test1@example.com',
            password='testpass123',
            nom='Testt',
            prenom='User',
            role='EXPERT'
        )
        
        self.projet = Projet.objects.create(
            nom='Projet Test',
            statut='EN_COURS',
            responsable=self.user
        )
        
        self.alerte = Alerte.objects.create(
            projet=self.projet,
            type_alerte='TEST',
            niveau='INFO',
            message='Test alerte'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_list_alertes(self):
        """Test de récupération de la liste des alertes"""
        url = reverse('alerts:alerte-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type_alerte'], 'TEST')
    
    def test_create_alerte(self):
        """Test de création d'alerte via API"""
        url = reverse('alerts:alerte-list-create')
        data = {
            'projet': self.projet.id,
            'type_alerte': 'NOUVEAU_TEST',
            'niveau': 'WARNING',
            'message': 'Nouvelle alerte de test'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alerte.objects.count(), 2)
    
    def test_marquer_alerte_lue(self):
        """Test de marquage d'alerte comme lue"""
        url = reverse('alerts:marquer-alerte-lue', kwargs={'pk': self.alerte.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.alerte.refresh_from_db()
        self.assertEqual(self.alerte.statut, 'LU')
        self.assertEqual(self.alerte.lue_par, self.user)
        self.assertIsNotNone(self.alerte.date_lecture)
    
    def test_marquer_alerte_traitee(self):
        """Test de marquage d'alerte comme traitée"""
        url = reverse('alerts:marquer-alerte-traitee', kwargs={'pk': self.alerte.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.alerte.refresh_from_db()
        self.assertEqual(self.alerte.statut, 'TRAITEE')
    
    def test_statistiques_alertes(self):
        """Test de récupération des statistiques"""
        # Créer quelques alertes supplémentaires
        Alerte.objects.create(
            projet=self.projet,
            type_alerte='CRITIQUE_TEST',
            niveau='CRITIQUE',
            message='Alerte critique'
        )
        
        url = reverse('alerts:statistiques-alertes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_alertes'], 2)
        self.assertEqual(response.data['alertes_critiques'], 1)
    
    def test_filtrage_alertes(self):
        """Test du filtrage des alertes"""
        # Créer une alerte critique
        Alerte.objects.create(
            projet=self.projet,
            type_alerte='CRITIQUE_TEST',
            niveau='CRITIQUE',
            message='Alerte critique'
        )
        
        url = reverse('alerts:alerte-list-create')
        
        # Filtrer par niveau
        response = self.client.get(url, {'niveau': 'CRITIQUE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['niveau'], 'CRITIQUE')
        
        # Filtrer par projet
        response = self.client.get(url, {'projet': self.projet.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_detecter_alertes_automatiques(self):
        """Test de détection automatique des alertes"""
        # Modifier le projet pour déclencher une alerte
        self.projet.budget_initial = Decimal('100000.00')
        self.projet.cout_actuel = Decimal('95000.00')
        self.projet.seuil_alerte_cout = Decimal('80.00')
        self.projet.save()
        
        url = reverse('alerts:detecter-alertes-automatiques')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifier qu'au moins une alerte a été créée
        self.assertTrue('alertes' in response.data)


class AlerteAuthenticationTest(APITestCase):
    """Tests d'authentification pour les alertes"""
    
    def test_access_sans_authentification(self):
        """Test d'accès sans authentification"""
        url = reverse('alerts:alerte-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_access_avec_authentification(self):
        """Test d'accès avec authentification"""
        user = User.objects.create_user(
            email='test1@example.com',
            password='testpass123',
            nom='Testt',
            prenom='User',
            role='EXPERT'
        )
        
        self.client.force_authenticate(user=user)
        
        url = reverse('alerts:alerte-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)