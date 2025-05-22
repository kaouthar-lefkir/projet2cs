from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from PetroMonitore.models import Projet, Phase, Operation, Utilisateur
from PetroMonitore.serializers import (
    PhaseSerializer, 
    PhaseCreateSerializer, 
    PhaseUpdateSerializer,
    OperationSerializer, 
    OperationCreateSerializer, 
    OperationUpdateSerializer
)

class PhaseModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
    
    def test_phase_creation(self):
        """
        Test creating a Phase
        """
        phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            description='Test Phase Description',
            ordre=1,
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30),
            budget_alloue=Decimal('10000.00'),
            statut='PLANIFIE'
        )
        
        self.assertEqual(phase.projet, self.projet)
        self.assertEqual(phase.nom, 'Test Phase')
        self.assertEqual(phase.ordre, 1)
        self.assertEqual(phase.statut, 'PLANIFIE')
        self.assertEqual(phase.progression, Decimal('0'))
    
    def test_phase_ordering(self):
        """
        Test Phase ordering
        """
        phase1 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            ordre=1,
            statut='PLANIFIE'
        )
        phase2 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            ordre=2,
            statut='PLANIFIE'
        )
        
        phases = Phase.objects.filter(projet=self.projet).order_by('ordre')
        self.assertEqual(list(phases), [phase1, phase2])


class OperationModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        # Create a test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            ordre=1,
            statut='PLANIFIE'
        )
    
    def test_operation_creation(self):
        """
        Test creating an Operation
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Test Operation',
            description='Test Operation Description',
            type_operation='TEST',
            date_debut_prevue=date.today(),
            date_fin_prevue=date.today() + timedelta(days=10),
            cout_prevue=Decimal('5000.00'),
            statut='PLANIFIE',
            responsable=self.user
        )
        
        self.assertEqual(operation.phase, self.phase)
        self.assertEqual(operation.nom, 'Test Operation')
        self.assertEqual(operation.statut, 'PLANIFIE')
        self.assertEqual(operation.progression, Decimal('0'))


class PhaseSerializerTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        # Create a test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            ordre=1,
            statut='PLANIFIE'
        )
    
    def test_phase_serializer(self):
        """
        Test PhaseSerializer
        """
        serializer = PhaseSerializer(self.phase)
        data = serializer.data
        
        self.assertEqual(set(data.keys()), set([
            'id', 'projet', 'nom', 'description', 'ordre', 
            'date_debut_prevue', 'date_fin_prevue', 
            'date_debut_reelle', 'date_fin_reelle', 
            'budget_alloue', 'cout_actuel', 
            'progression', 'statut', 'operations'
        ]))
    
    def test_phase_create_serializer(self):
        """
        Test PhaseCreateSerializer
        """
        data = {
            'projet': self.projet.id,
            'nom': 'New Phase',
            'ordre': 2,
            'statut': 'PLANIFIE'
        }
        serializer = PhaseCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        phase = serializer.save()
        
        self.assertEqual(phase.nom, 'New Phase')
        self.assertEqual(phase.projet, self.projet)


class OperationSerializerTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        # Create a test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            ordre=1,
            statut='PLANIFIE'
        )
    
    def test_operation_serializer(self):
        """
        Test OperationSerializer
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Test Operation',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        serializer = OperationSerializer(operation)
        data = serializer.data
        
        self.assertEqual(set(data.keys()), set([
            'id', 'phase', 'nom', 'description', 'type_operation', 
            'date_debut_prevue', 'date_fin_prevue', 
            'date_debut_reelle', 'date_fin_reelle', 
            'cout_prevue', 'cout_reel', 'progression', 
            'statut', 'responsable'
        ]))
    
    def test_operation_create_serializer(self):
        """
        Test OperationCreateSerializer
        """
        data = {
            'phase': self.phase.id,
            'nom': 'New Operation',
            'statut': 'PLANIFIE'
        }
        serializer = OperationCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        operation = serializer.save()
        
        self.assertEqual(operation.nom, 'New Operation')
        self.assertEqual(operation.phase, self.phase)


class PhaseAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
    
    def test_create_phase(self):
        """
        Test creating a phase via API
        """
        url = reverse('phase-list', kwargs={'projet_id': self.projet.id})
        data = {
            'nom': 'New Phase',
            'ordre': 1,
            'statut': 'PLANIFIE'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Phase.objects.count(), 1)
        self.assertEqual(Phase.objects.first().nom, 'New Phase')
    
    def test_list_phases(self):
        """
        Test listing phases for a project
        """
        # Create some test phases
        Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            ordre=1,
            statut='PLANIFIE'
        )
        Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            ordre=2,
            statut='PLANIFIE'
        )
        
        url = reverse('phase-list', kwargs={'projet_id': self.projet.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_update_phase(self):
        """
        Test updating a phase
        """
        phase = Phase.objects.create(
            projet=self.projet,
            nom='Original Phase',
            ordre=1,
            statut='PLANIFIE'
        )
        
        url = reverse('phase-detail', kwargs={'pk': phase.id})
        data = {
            'nom': 'Updated Phase',
            'statut': 'EN_COURS'
        }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        phase.refresh_from_db()
        self.assertEqual(phase.nom, 'Updated Phase')
        self.assertEqual(phase.statut, 'EN_COURS')
    
    def test_delete_phase(self):
        """
        Test deleting a phase
        """
        phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase to Delete',
            ordre=1,
            statut='PLANIFIE'
        )
        
        url = reverse('phase-detail', kwargs={'pk': phase.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Phase.objects.count(), 0)


class OperationAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        # Create a test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            ordre=1,
            statut='PLANIFIE'
        )
    
    def test_create_operation(self):
        """
        Test creating an operation via API
        """
        url = reverse('operation-list', kwargs={'phase_id': self.phase.id})
        data = {
            'nom': 'New Operation',
            'statut': 'PLANIFIE'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Operation.objects.count(), 1)
        self.assertEqual(Operation.objects.first().nom, 'New Operation')
    
    def test_list_operations(self):
        """
        Test listing operations for a phase
        """
        # Create some test operations
        Operation.objects.create(
            phase=self.phase,
            nom='Operation 1',
            statut='PLANIFIE',
            responsable=self.user
        )
        Operation.objects.create(
            phase=self.phase,
            nom='Operation 2',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-list', kwargs={'phase_id': self.phase.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_update_operation(self):
        """
        Test updating an operation
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Original Operation',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-detail', kwargs={'pk': operation.id})
        data = {
            'nom': 'Updated Operation',
            'statut': 'EN_COURS'
        }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operation.refresh_from_db()
        self.assertEqual(operation.nom, 'Updated Operation')
        self.assertEqual(operation.statut, 'EN_COURS')
    
    def test_delete_operation(self):
        """
        Test deleting an operation
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Operation to Delete',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-detail', kwargs={'pk': operation.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Operation.objects.count(), 0)
    
    def test_update_operation_progression(self):
        """
        Test updating operation progression
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Test Operation',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-progression', kwargs={'pk': operation.id})
        data = {
            'progression': 50
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operation.refresh_from_db()
        self.assertEqual(operation.progression, 50)
        self.assertIsNotNone(operation.date_debut_reelle)
    
    def test_update_operation_progression_complete(self):
        """
        Test updating operation progression to 100%
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Test Operation',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-progression', kwargs={'pk': operation.id})
        data = {
            'progression': 100
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operation.refresh_from_db()
        self.assertEqual(operation.progression, 100)
        self.assertIsNotNone(operation.date_debut_reelle)
        self.assertIsNotNone(operation.date_fin_reelle)
    
    def test_update_operation_progression_invalid(self):
        """
        Test updating operation progression with invalid values
        """
        operation = Operation.objects.create(
            phase=self.phase,
            nom='Test Operation',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-progression', kwargs={'pk': operation.id})
        
        # Test negative progression
        response = self.client.post(url, {'progression': -10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test progression > 100
        response = self.client.post(url, {'progression': 110})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid progression value
        response = self.client.post(url, {'progression': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PhaseOrderingAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
    
    def test_phase_ordering(self):
        """
        Test reordering phases
        """
        # Create some test phases
        phase1 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            ordre=1,
            statut='PLANIFIE'
        )
        phase2 = Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            ordre=2,
            statut='PLANIFIE'
        )
        
        url = reverse('phase-ordering', kwargs={'projet_id': self.projet.id})
        data = {
            'phases': [
                {'id': phase2.id, 'ordre': 1},
                {'id': phase1.id, 'ordre': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh phases from database
        phase1.refresh_from_db()
        phase2.refresh_from_db()
        
        # Verify new order
        self.assertEqual(phase2.ordre, 1)
        self.assertEqual(phase1.ordre, 2)


class OperationOrderingAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Utilisateur.objects.create_user(
            email='test@example.com', 
            password='testpassword', 
            nom='Test', 
            prenom='User',
            role='TOP_MANAGEMENT'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test project
        self.projet = Projet.objects.create(
            nom='Test Project',
            description='Test Project Description',
            statut='PLANIFIE',
            responsable=self.user
        )
        
        # Create a test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Test Phase',
            ordre=1,
            statut='PLANIFIE'
        )
    
    def test_operation_ordering(self):
        """
        Test reordering operations
        """
        # Create some test operations
        operation1 = Operation.objects.create(
            phase=self.phase,
            nom='Operation 1',
            date_debut_prevue=date.today(),
            statut='PLANIFIE',
            responsable=self.user
        )
        operation2 = Operation.objects.create(
            phase=self.phase,
            nom='Operation 2',
            date_debut_prevue=date.today() + timedelta(days=1),
            statut='PLANIFIE',
            responsable=self.user
        )
        
        url = reverse('operation-ordering', kwargs={'phase_id': self.phase.id})
        data = {
            'operations': [
                {
                    'id': operation2.id, 
                    'date_debut_prevue': str(date.today())
                },
                {
                    'id': operation1.id, 
                    'date_debut_prevue': str(date.today() + timedelta(days=1))
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh operations from database
        operation1.refresh_from_db()
        operation2.refresh_from_db()
        
        # Verify new dates
        self.assertEqual(str(operation2.date_debut_prevue), str(date.today()))
        self.assertEqual(str(operation1.date_debut_prevue), str(date.today() + timedelta(days=1)))