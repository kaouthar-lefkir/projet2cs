
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from ..models import (
    Operation, Phase, Projet, Seuil, HistoriqueModification, Utilisateur
)
from ..serializers import (
    SeuilSerializer, HistoriqueModificationSeuilSerializer
)

User = get_user_model()


class SeuilSerializerTestCase(TestCase):
    """Tests unitaires pour le SerializerMethodField de Seuil"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer une opération
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Opération Test',
            statut='EN_COURS'
        )
        
        # Créer un seuil
        self.seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # Simuler une modification du seuil
        self.seuil.valeur_verte = Decimal('15.00')
        self.seuil.modifie_par = self.user
        self.seuil.date_modification = timezone.now()
        self.seuil.save()

    def test_seuil_serializer_fields(self):
        """Test que le sérialiseur inclut tous les champs attendus"""
        serializer = SeuilSerializer(instance=self.seuil)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('operation', data)
        self.assertIn('valeur_verte', data)
        self.assertIn('valeur_jaune', data)
        self.assertIn('valeur_rouge', data)
        self.assertIn('date_definition', data)
        self.assertIn('defini_par', data)
        self.assertIn('defini_par_nom', data)
        self.assertIn('date_modification', data)
        self.assertIn('modifie_par', data)
        self.assertIn('modifie_par_nom', data)
        self.assertIn('statut_couleur', data)
    
    def test_get_defini_par_nom(self):
        """Test que le nom complet du créateur est correctement retourné"""
        serializer = SeuilSerializer(instance=self.seuil)
        self.assertEqual(serializer.data['defini_par_nom'], 'Jean Dupont')
    
    def test_get_modifie_par_nom(self):
        """Test que le nom complet du modificateur est correctement retourné"""
        serializer = SeuilSerializer(instance=self.seuil)
        self.assertEqual(serializer.data['modifie_par_nom'], 'Jean Dupont')
    
    def test_to_representation_conversion(self):
        """Test que les valeurs décimales sont converties en entiers"""
        serializer = SeuilSerializer(instance=self.seuil)
        self.assertEqual(serializer.data['valeur_verte'], 15)
        self.assertEqual(serializer.data['valeur_jaune'], 20)
        self.assertEqual(serializer.data['valeur_rouge'], 30)
    
    def test_validate_thresholds_order(self):
        """Test que la validation des seuils respecte l'ordre croissant"""
        serializer = SeuilSerializer(data={
            'operation': self.operation.id,
            'valeur_verte': 30,
            'valeur_jaune': 20,
            'valeur_rouge': 40
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
        serializer = SeuilSerializer(data={
            'operation': self.operation.id,
            'valeur_verte': 10,
            'valeur_jaune': 20,
            'valeur_rouge': 15
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        
        serializer = SeuilSerializer(data={
            'operation': self.operation.id,
            'valeur_verte': 10,
            'valeur_jaune': 20,
            'valeur_rouge': 30
        })
        
        self.assertTrue(serializer.is_valid())
    
    def test_update_with_modified_by(self):
        """Test que date_modification est définie lors de la mise à jour"""
        another_user = User.objects.create_user(
            email='autre@example.com',
            password='password123',
            nom='Martin',
            prenom='Pierre'
        )
        
        serializer = SeuilSerializer(instance=self.seuil, data={
            'operation': self.operation.id,
            'valeur_verte': 15,
            'valeur_jaune': 25,
            'valeur_rouge': 35,
            'modifie_par': another_user.id
        }, partial=True)
        
        self.assertTrue(serializer.is_valid())
        seuil_mis_a_jour = serializer.save()
        self.assertIsNotNone(seuil_mis_a_jour.date_modification)


class HistoriqueModificationSeuilSerializerTestCase(TestCase):
    """Tests unitaires pour le sérialiseur HistoriqueModificationSeuil"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer une opération
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Opération Test',
            statut='EN_COURS'
        )
        
        # Créer un seuil
        self.seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # Créer une entrée dans l'historique
        self.historique = HistoriqueModification.objects.create(
            table_modifiee='Seuil',
            id_enregistrement=self.seuil.id,
            champ_modifie='valeur_verte',
            ancienne_valeur='10.00',
            nouvelle_valeur='15.00',
            modifie_par=self.user,
            commentaire='Modification test'
        )
    
    def test_historique_serializer_fields(self):
        """Test que le sérialiseur inclut tous les champs attendus"""
        serializer = HistoriqueModificationSeuilSerializer(instance=self.historique)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('table_modifiee', data)
        self.assertIn('id_enregistrement', data)
        self.assertIn('champ_modifie', data)
        self.assertIn('ancienne_valeur', data)
        self.assertIn('nouvelle_valeur', data)
        self.assertIn('date_modification', data)
        self.assertIn('modifie_par', data)
        self.assertIn('modifie_par_nom', data)
        self.assertIn('commentaire', data)
    
    def test_get_modifie_par_nom(self):
        """Test que le nom complet du modificateur est correctement retourné"""
        serializer = HistoriqueModificationSeuilSerializer(instance=self.historique)
        self.assertEqual(serializer.data['modifie_par_nom'], 'Jean Dupont')
    
    def test_null_modifie_par(self):
        """Test le comportement quand modifie_par est null"""
        self.historique.modifie_par = None
        self.historique.save()
        
        serializer = HistoriqueModificationSeuilSerializer(instance=self.historique)
        self.assertIsNone(serializer.data['modifie_par_nom'])


class SeuilListCreateViewTestCase(APITestCase):
    """Tests unitaires pour la vue SeuilListCreateView"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Créer un deuxième utilisateur
        self.user2 = User.objects.create_user(
            email='test2@example.com',
            password='password123',
            nom='Martin',
            prenom='Pierre'
        )
        
        # Authentifier l'utilisateur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer deux opérations
        self.operation1 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 1',
            statut='EN_COURS'
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 2',
            statut='EN_COURS'
        )
        
        # Créer un seuil
        self.seuil = Seuil.objects.create(
            operation=self.operation1,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # URL pour les tests
        self.list_url = reverse('seuil-list')
    
    def test_list_seuils(self):
        """Test la récupération de la liste des seuils"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_seuil(self):
        """Test la création d'un nouveau seuil"""
        data = {
            'operation': self.operation2.id,
            'valeur_verte': 15,
            'valeur_jaune': 25,
            'valeur_rouge': 35
        }
        
        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seuil.objects.count(), 2)
        
        # Vérifier que l'historique a été créé
        historique = HistoriqueModification.objects.filter(
            table_modifiee='Seuil',
            id_enregistrement=response.data['id']
        )
        self.assertEqual(historique.count(), 1)
    
    def test_search_filter(self):
        """Test le filtrage par recherche"""
        response = self.client.get(f"{self.list_url}?search=Opération 1")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['operation'], self.operation1.id)
        
        response = self.client.get(f"{self.list_url}?search=inexistant")
        self.assertEqual(len(response.data), 0)
    
    def test_ordering_filter(self):
        """Test le tri des résultats"""
        # Créer un second seuil avec une date différente
        seuil2 = Seuil.objects.create(
            operation=self.operation2,
            valeur_verte=Decimal('15.00'),
            valeur_jaune=Decimal('25.00'),
            valeur_rouge=Decimal('35.00'),
            defini_par=self.user,
            date_definition=timezone.now() + timezone.timedelta(days=1)
        )
        
        # Récupérer les IDs pour une comparaison plus fiable
        seuil1_id = self.seuil.id
        operation1_id = self.operation1.id
        operation2_id = self.operation2.id
        
        # Tri ascendant
        response = self.client.get(f"{self.list_url}?ordering=date_definition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Vérifier que le seuil lié à operation1 est bien le premier dans le résultat
        self.assertEqual(response.data[0]['id'], seuil1_id)
        self.assertEqual(response.data[0]['operation'], operation1_id)
        
        # Tri descendant
        response = self.client.get(f"{self.list_url}?ordering=-date_definition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le seuil lié à operation2 est bien le premier dans le résultat
        self.assertEqual(response.data[0]['id'], seuil2.id)
        self.assertEqual(response.data[0]['operation'], operation2_id)
        
        # Tri ascendant
        response = self.client.get(f"{self.list_url}?ordering=date_definition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['operation'], self.operation1.id)
        
        # Tri descendant
        response = self.client.get(f"{self.list_url}?ordering=-date_definition")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['operation'], self.operation2.id)
    
    def test_unauthorised_access(self):
        """Test l'accès non autorisé"""
        # Déconnecter l'utilisateur
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SeuilDetailViewTestCase(APITestCase):
    """Tests unitaires pour la vue SeuilDetailView"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Authentifier l'utilisateur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer une opération
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Opération Test',
            statut='EN_COURS'
        )
        
        # Créer un seuil
        self.seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # URL pour les tests
        self.detail_url = reverse('seuil-detail', kwargs={'pk': self.seuil.pk})
    
    def test_retrieve_seuil(self):
        """Test la récupération d'un seuil spécifique"""
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.seuil.id)
    
    def test_update_seuil(self):
        """Test la mise à jour d'un seuil"""
        data = {
            'operation': self.operation.id,
            'valeur_verte': 15,
            'valeur_jaune': 25,
            'valeur_rouge': 35
        }
        
        response = self.client.put(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.seuil.refresh_from_db()
        self.assertEqual(self.seuil.valeur_verte, Decimal('15'))
        
        # Vérifier que l'historique a été créé
        historique = HistoriqueModification.objects.filter(
            table_modifiee='Seuil',
            id_enregistrement=self.seuil.id,
            champ_modifie='valeur_verte'
        )
        self.assertEqual(historique.count(), 1)
    
    def test_partial_update_seuil(self):
        """Test la mise à jour partielle d'un seuil"""
        data = {
            'valeur_verte': 15
        }
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.seuil.refresh_from_db()
        self.assertEqual(self.seuil.valeur_verte, Decimal('15'))
        self.assertEqual(self.seuil.valeur_jaune, Decimal('20'))
        self.assertEqual(self.seuil.valeur_rouge, Decimal('30'))
    
    def test_delete_seuil(self):
        """Test la suppression d'un seuil"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Seuil.objects.count(), 0)
    
    def test_unauthorized_access(self):
        """Test l'accès non autorisé"""
        # Déconnecter l'utilisateur
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.put(self.detail_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.patch(self.detail_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SeuilHistoriqueViewTestCase(APITestCase):
    """Tests unitaires pour la vue SeuilHistoriqueView"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Authentifier l'utilisateur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer une opération
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom='Opération Test',
            statut='EN_COURS'
        )
        
        # Créer un seuil
        self.seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # Créer des entrées dans l'historique
        for i in range(3):
            HistoriqueModification.objects.create(
                table_modifiee='Seuil',
                id_enregistrement=self.seuil.id,
                champ_modifie=f'valeur_test_{i}',
                ancienne_valeur=f'old_{i}',
                nouvelle_valeur=f'new_{i}',
                modifie_par=self.user,
                commentaire=f'Modification test {i}'
            )
        
        # Créer une entrée pour un autre seuil (fictif)
        HistoriqueModification.objects.create(
            table_modifiee='Seuil',
            id_enregistrement=9999,  # ID inexistant
            champ_modifie='valeur_test',
            ancienne_valeur='old',
            nouvelle_valeur='new',
            modifie_par=self.user,
            commentaire='Modification autre seuil'
        )
        
        # URL pour les tests
        self.historique_url = reverse('seuil-historique', kwargs={'pk': self.seuil.pk})
    
    def test_get_historique(self):
        """Test la récupération de l'historique d'un seuil spécifique"""
        response = self.client.get(self.historique_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Seulement les entrées du seuil demandé
    
    def test_unauthorized_access(self):
        """Test l'accès non autorisé"""
        # Déconnecter l'utilisateur
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.historique_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SeuilOperationViewTestCase(APITestCase):
    """Tests unitaires pour la vue SeuilOperationView"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            nom='Dupont',
            prenom='Jean'
        )
        
        # Authentifier l'utilisateur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description test',
            statut='EN_COURS'
        )
        
        # Créer une phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            ordre=1,
            statut='EN_COURS'
        )
        
        # Créer deux opérations
        self.operation1 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 1',
            statut='EN_COURS'
        )
        
        self.operation2 = Operation.objects.create(
            phase=self.phase,
            nom='Opération 2',
            statut='EN_COURS'
        )
        
        # Créer un seuil pour l'opération1
        self.seuil = Seuil.objects.create(
            operation=self.operation1,
            valeur_verte=Decimal('10.00'),
            valeur_jaune=Decimal('20.00'),
            valeur_rouge=Decimal('30.00'),
            defini_par=self.user,
            date_definition=timezone.now()
        )
        
        # URL pour les tests
    
    def test_get_seuil_for_operation(self):
        """Test la récupération du seuil pour une opération spécifique"""
        url = reverse('seuil-operation', kwargs={'operation_id': self.operation1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.seuil.id)
    
    def test_missing_operation_id(self):
        """Test la requête sans operation_id"""
        url = reverse('seuil-operation', kwargs={'operation_id': 999})  # Non-existent ID
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_operation_not_found(self):
        """Test la récupération pour une opération sans seuil"""
        url = reverse('seuil-operation', kwargs={'operation_id': self.operation2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_unauthorized_access(self):
        """Test l'accès non autorisé"""
        # Déconnecter l'utilisateur
        self.client.force_authenticate(user=None)
        url = reverse('seuil-operation', kwargs={'operation_id': self.operation1.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class SeuilViewsTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            nom='Test',
            prenom='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test project
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description projet test",
            statut="EN_COURS",
            responsable=self.user
        )
        
        # Create test phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        # Create test operation
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Operation Test",
            statut="EN_COURS",
            responsable=self.user
        )
        
        # URLs
        self.initialiser_seuil_url = reverse('seuil-initialiser-operation')
        self.historique_seuil_list_url = reverse('historique-seuil-list')
    
    def test_initialiser_seuil_success(self):
        """Test successful threshold initialization for an operation"""
        data = {
            'operation_id': self.operation.id,
            'valeur_verte': '85.00',
            'valeur_jaune': '70.00',
            'valeur_rouge': '50.00'
        }
        
        response = self.client.post(self.initialiser_seuil_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Seuil.objects.count(), 1)
        
        seuil = Seuil.objects.first()
        self.assertEqual(seuil.operation, self.operation)
        self.assertEqual(float(seuil.valeur_verte), float(data['valeur_verte']))
        self.assertEqual(float(seuil.valeur_jaune), float(data['valeur_jaune']))
        self.assertEqual(float(seuil.valeur_rouge), float(data['valeur_rouge']))
        self.assertEqual(seuil.defini_par, self.user)
        
        # Check if history record was created
        historique = HistoriqueModification.objects.filter(
            table_modifiee='Seuil',
            id_enregistrement=seuil.id
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertEqual(historique.modifie_par, self.user)
        self.assertEqual(historique.champ_modifie, 'création')
    
    def test_initialiser_seuil_missing_data(self):
        """Test threshold initialization with missing data"""
        data = {
            'operation_id': self.operation.id,
            'valeur_verte': '85.00',
            # Missing valeur_jaune and valeur_rouge
        }
        
        response = self.client.post(self.initialiser_seuil_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seuil.objects.count(), 0)
    
    def test_initialiser_seuil_operation_not_found(self):
        """Test threshold initialization with non-existent operation"""
        data = {
            'operation_id': 999,  # Non-existent ID
            'valeur_verte': '85.00',
            'valeur_jaune': '70.00',
            'valeur_rouge': '50.00'
        }
        
        response = self.client.post(self.initialiser_seuil_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Seuil.objects.count(), 0)
    
    def test_initialiser_seuil_already_exists(self):
        """Test threshold initialization when thresholds already exist for operation"""
        # Create seuil for operation
        Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('85.00'),
            valeur_jaune=Decimal('70.00'),
            valeur_rouge=Decimal('50.00'),
            defini_par=self.user
        )
        
        data = {
            'operation_id': self.operation.id,
            'valeur_verte': '90.00',
            'valeur_jaune': '75.00',
            'valeur_rouge': '60.00'
        }
        
        response = self.client.post(self.initialiser_seuil_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Seuil.objects.count(), 1)  # Count should still be 1
    
    def test_historique_seuil_list(self):
        """Test listing threshold modification history"""
        # Create seuil
        seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('85.00'),
            valeur_jaune=Decimal('70.00'),
            valeur_rouge=Decimal('50.00'),
            defini_par=self.user
        )
        
        # Create historique entries
        HistoriqueModification.objects.create(
            table_modifiee='Seuil',
            id_enregistrement=seuil.id,
            champ_modifie='création',
            nouvelle_valeur=f"Vert: {seuil.valeur_verte}, Jaune: {seuil.valeur_jaune}, Rouge: {seuil.valeur_rouge}",
            modifie_par=self.user,
            commentaire="Initialisation des seuils pour l'opération"
        )
        
        HistoriqueModification.objects.create(
            table_modifiee='Seuil',
            id_enregistrement=seuil.id,
            champ_modifie='valeur_verte',
            ancienne_valeur='85.00',
            nouvelle_valeur='90.00',
            modifie_par=self.user,
            commentaire="Modification seuil vert"
        )
        
        # Create another historique for a different table to test filtering
        HistoriqueModification.objects.create(
            table_modifiee='Operation',
            id_enregistrement=self.operation.id,
            champ_modifie='statut',
            ancienne_valeur='EN_COURS',
            nouvelle_valeur='TERMINE',
            modifie_par=self.user
        )
        
        response = self.client.get(self.historique_seuil_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only get the 2 Seuil entries, not the Operation one
        self.assertEqual(len(response.data), 2)
        
        # Test search filter
        search_url = f"{self.historique_seuil_list_url}?search=Modification seuil vert"
        response = self.client.get(search_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['commentaire'], "Modification seuil vert")
    
    def test_historique_seuil_detail(self):
        """Test retrieving specific threshold history record"""
        # Create seuil
        seuil = Seuil.objects.create(
            operation=self.operation,
            valeur_verte=Decimal('85.00'),
            valeur_jaune=Decimal('70.00'),
            valeur_rouge=Decimal('50.00'),
            defini_par=self.user
        )
        
        # Create historique entry
        historique = HistoriqueModification.objects.create(
            table_modifiee='Seuil',
            id_enregistrement=seuil.id,
            champ_modifie='création',
            nouvelle_valeur=f"Vert: {seuil.valeur_verte}, Jaune: {seuil.valeur_jaune}, Rouge: {seuil.valeur_rouge}",
            modifie_par=self.user,
            commentaire="Initialisation des seuils pour l'opération"
        )
        
        detail_url = reverse('historique-seuil-detail', kwargs={'pk': historique.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], historique.id)
        self.assertEqual(response.data['table_modifiee'], 'Seuil')
        self.assertEqual(response.data['champ_modifie'], 'création')
        self.assertEqual(response.data['commentaire'], "Initialisation des seuils pour l'opération")
    
    def test_historique_seuil_detail_not_found(self):
        """Test retrieving non-existent history record"""
        detail_url = reverse('historique-seuil-detail', kwargs={'pk': 999})  # Non-existent ID
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test access to views without authentication"""
        # Create an unauthenticated client
        client = APIClient()
        
        # Try to access the endpoints without authentication
        response1 = client.post(self.initialiser_seuil_url, {}, format='json')
        response2 = client.get(self.historique_seuil_list_url)
        
        # Both should require authentication
        self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)


class SeuilOperationHistoriqueIntegrationTest(APITestCase):
    """Integration tests between seuil initialization and history tracking"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            nom='Test',
            prenom='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create project structure
        self.projet = Projet.objects.create(
            nom="Projet Integration Test",
            statut="EN_COURS",
            responsable=self.user
        )
        
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Integration Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Operation Integration Test",
            statut="EN_COURS",
            responsable=self.user
        )
        
        # URLs
        self.initialiser_seuil_url = reverse('seuil-initialiser-operation')
        self.historique_seuil_list_url = reverse('historique-seuil-list')
    
    def test_seuil_creation_updates_historique(self):
        """Test that creating a seuil through the API properly creates history entries"""
        data = {
            'operation_id': self.operation.id,
            'valeur_verte': '95.00',
            'valeur_jaune': '80.00',
            'valeur_rouge': '60.00'
        }
        
        # First check that there are no seuils or historique records
        self.assertEqual(Seuil.objects.count(), 0)
        self.assertEqual(HistoriqueModification.objects.count(), 0)
        
        # Create seuil via API
        response = self.client.post(self.initialiser_seuil_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that both seuil and historique were created
        self.assertEqual(Seuil.objects.count(), 1)
        self.assertEqual(HistoriqueModification.objects.count(), 1)
        
        # Get the created seuil
        seuil = Seuil.objects.first()
        
        # Get the historique record and verify its contents
        historique = HistoriqueModification.objects.first()
        self.assertEqual(historique.table_modifiee, 'Seuil')
        self.assertEqual(historique.id_enregistrement, seuil.id)
        self.assertEqual(historique.champ_modifie, 'création')
        self.assertIn(str(seuil.valeur_verte), historique.nouvelle_valeur)
        self.assertIn(str(seuil.valeur_jaune), historique.nouvelle_valeur)
        self.assertIn(str(seuil.valeur_rouge), historique.nouvelle_valeur)
        self.assertEqual(historique.modifie_par, self.user)
        
        # Get historique from API and verify content matches
        response = self.client.get(self.historique_seuil_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        api_historique = response.data[0]
        self.assertEqual(api_historique['table_modifiee'], 'Seuil')
        self.assertEqual(api_historique['id_enregistrement'], seuil.id)
        self.assertEqual(api_historique['champ_modifie'], 'création')