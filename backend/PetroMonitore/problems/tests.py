from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json
from datetime import datetime, timedelta
from decimal import Decimal

from ..models import (
    Utilisateur, Projet, Phase, Operation, Probleme, Solution, 
    Rapport, HistoriqueModification
)
from .serializers import (
    UtilisateurMinSerializer, ProblemeListSerializer, ProblemeDetailSerializer,
    ProblemeCreateSerializer, ProblemeUpdateSerializer, 
    SolutionListSerializer, SolutionCreateSerializer, SolutionUpdateSerializer
)
from .utils import track_probleme_status_change, track_solution_status_change, get_probleme_statistics

class ModelTests(TestCase):
    def setUp(self):
        # Create utilisateur
        self.utilisateur = Utilisateur.objects.create(
            email="test@example.com",
            nom="Doe",
            prenom="John",
            role="INGENIEUR_TERRAIN"
        )
        self.utilisateur.set_password("password123")
        self.utilisateur.save()
        
        # Create projet
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        # Create phase
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        # Create operation
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Operation Test",
            statut="EN_COURS"
        )
        
        # Create rapport
        self.rapport = Rapport.objects.create(
            projet=self.projet,
            type_rapport="Rapport Test",
            importe_par=self.utilisateur
        )
        
        # Create probleme
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
        
        # Create solution
        self.solution = Solution.objects.create(
            probleme=self.probleme,
            description="Description de la solution test",
            type_solution="Correctif",
            cout_estime=Decimal("1000.00"),
            delai_estime=5,
            proposee_par=self.utilisateur
        )

    def test_utilisateur_creation(self):
        """Test utilisateur creation and methods"""
        self.assertEqual(self.utilisateur.get_full_name(), "John Doe")
        self.assertEqual(self.utilisateur.get_role(), "INGENIEUR_TERRAIN")
        self.assertTrue(self.utilisateur.check_password("password123"))
    
    def test_projet_creation(self):
        """Test projet creation"""
        self.assertEqual(str(self.projet), "Projet Test")
        self.assertEqual(self.projet.statut, "EN_COURS")
    
    def test_phase_creation(self):
        """Test phase creation"""
        self.assertEqual(str(self.phase), "Projet Test - Phase Test")
        self.assertEqual(self.phase.projet, self.projet)
    
    def test_operation_creation(self):
        """Test operation creation"""
        self.assertEqual(str(self.operation), "Phase Test - Operation Test")
        self.assertEqual(self.operation.phase, self.phase)
    
    def test_probleme_creation(self):
        """Test probleme creation"""
        self.assertEqual(str(self.probleme), "Problème Test")
        self.assertEqual(self.probleme.projet, self.projet)
        self.assertEqual(self.probleme.signale_par, self.utilisateur)
    
    def test_solution_creation(self):
        """Test solution creation"""
        self.assertEqual(self.solution.probleme, self.probleme)
        self.assertEqual(self.solution.proposee_par, self.utilisateur)
        self.assertEqual(self.solution.statut, "PROPOSEE")


class SerializerTests(TestCase):
    def setUp(self):
        # Create test data
        self.utilisateur = Utilisateur.objects.create(
            email="test@example.com",
            nom="Doe",
            prenom="John",
            role="INGENIEUR_TERRAIN"
        )
        self.utilisateur.set_password("password123")
        self.utilisateur.save()
        
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Operation Test",
            statut="EN_COURS"
        )
        
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
        
        self.solution = Solution.objects.create(
            probleme=self.probleme,
            description="Description de la solution test",
            type_solution="Correctif",
            cout_estime=Decimal("1000.00"),
            delai_estime=5,
            proposee_par=self.utilisateur
        )

    def test_utilisateur_min_serializer(self):
        """Test UtilisateurMinSerializer"""
        serializer = UtilisateurMinSerializer(self.utilisateur)
        self.assertEqual(serializer.data['nom_complet'], "John Doe")
        self.assertEqual(serializer.data['email'], "test@example.com")
        self.assertEqual(serializer.data['role'], "INGENIEUR_TERRAIN")
    
    def test_probleme_list_serializer(self):
        """Test ProblemeListSerializer"""
        serializer = ProblemeListSerializer(self.probleme)
        self.assertEqual(serializer.data['titre'], "Problème Test")
        self.assertEqual(serializer.data['statut'], "OUVERT")
        self.assertEqual(serializer.data['gravite'], "MOYENNE")
        self.assertEqual(serializer.data['signale_par_nom'], "John Doe")
        self.assertEqual(serializer.data['projet_nom'], "Projet Test")
        self.assertEqual(serializer.data['phase_nom'], "Phase Test")
        self.assertEqual(serializer.data['operation_nom'], "Operation Test")
        self.assertEqual(serializer.data['nb_solutions'], 1)
    
    def test_probleme_detail_serializer(self):
        """Test ProblemeDetailSerializer"""
        serializer = ProblemeDetailSerializer(self.probleme)
        self.assertEqual(serializer.data['titre'], "Problème Test")
        self.assertEqual(serializer.data['description'], "Description du problème test")
        self.assertEqual(len(serializer.data['solutions']), 1)
        self.assertEqual(serializer.data['signale_par']['nom_complet'], "John Doe")
    
    def test_probleme_create_serializer_validation(self):
        """Test ProblemeCreateSerializer validation"""
        # Test with invalid phase (not in the same projet)
        autre_projet = Projet.objects.create(
            nom="Autre Projet",
            statut="EN_COURS"
        )
        autre_phase = Phase.objects.create(
            projet=autre_projet,
            nom="Autre Phase",
            ordre=1,
            statut="EN_COURS"
        )
        
        data = {
            'titre': 'Nouveau Problème',
            'description': 'Description du nouveau problème',
            'gravite': 'MOYENNE',
            'statut': 'OUVERT',
            'projet': self.projet.id,
            'phase': autre_phase.id
        }
        
        serializer = ProblemeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phase', serializer.errors)
    
    def test_solution_list_serializer(self):
        """Test SolutionListSerializer"""
        serializer = SolutionListSerializer(self.solution)
        self.assertEqual(serializer.data['description'], "Description de la solution test")
        self.assertEqual(serializer.data['type_solution'], "Correctif")
        self.assertEqual(serializer.data['statut'], "PROPOSEE")
        self.assertEqual(serializer.data['proposee_par_nom'], "John Doe")
        self.assertEqual(serializer.data['probleme_titre'], "Problème Test")
    
    def test_solution_update_serializer(self):
        """Test SolutionUpdateSerializer"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Create a mock request with the user
        request = MockRequest(self.utilisateur)
        
        # Test updating solution status to VALIDEE
        data = {'statut': 'VALIDEE'}
        serializer = SolutionUpdateSerializer(
            instance=self.solution, 
            data=data, 
            context={'request': request},
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
        updated_solution = serializer.save()
        
        # Check that validation fields are updated
        self.assertEqual(updated_solution.statut, 'VALIDEE')
        self.assertEqual(updated_solution.validee_par, self.utilisateur)
        self.assertIsNotNone(updated_solution.date_validation)


class UtilsTests(TestCase):
    def setUp(self):
        # Create test data
        self.utilisateur = Utilisateur.objects.create(
            email="test@example.com",
            nom="Doe",
            prenom="John",
            role="INGENIEUR_TERRAIN"
        )
        
        self.projet = Projet.objects.create(
            nom="Projet Test",
            statut="EN_COURS"
        )
        
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        self.probleme = Probleme.objects.create(
            projet=self.projet,
            titre="Problème Test",
            gravite="MOYENNE",
            statut="OUVERT",
            signale_par=self.utilisateur
        )
        
        self.solution = Solution.objects.create(
            probleme=self.probleme,
            description="Description de la solution test",
            statut="PROPOSEE",
            proposee_par=self.utilisateur
        )

    def test_track_probleme_status_change(self):
        """Test tracking probleme status change"""
        old_status = self.probleme.statut
        new_status = "EN_COURS"
        
        # Track the change
        result = track_probleme_status_change(
            probleme_id=self.probleme.id,
            old_status=old_status,
            new_status=new_status,
            user=self.utilisateur
        )
        
        self.assertTrue(result)
        
        # Check if an entry was created in HistoriqueModification
        historique = HistoriqueModification.objects.filter(
            table_modifiee='Probleme',
            id_enregistrement=self.probleme.id,
            champ_modifie='statut'
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertEqual(historique.ancienne_valeur, old_status)
        self.assertEqual(historique.nouvelle_valeur, new_status)
        self.assertEqual(historique.modifie_par, self.utilisateur)
    
    def test_track_solution_status_change(self):
        """Test tracking solution status change"""
        old_status = self.solution.statut
        new_status = "MISE_EN_OEUVRE"
        
        # Track the change
        result = track_solution_status_change(
            solution_id=self.solution.id,
            old_status=old_status,
            new_status=new_status,
            user=self.utilisateur
        )
        
        self.assertTrue(result)
        
        # Check if an entry was created in HistoriqueModification for the solution
        historique_solution = HistoriqueModification.objects.filter(
            table_modifiee='Solution',
            id_enregistrement=self.solution.id,
            champ_modifie='statut'
        ).first()
        
        self.assertIsNotNone(historique_solution)
        self.assertEqual(historique_solution.ancienne_valeur, old_status)
        self.assertEqual(historique_solution.nouvelle_valeur, new_status)
        
        # Check if probleme status was updated to EN_COURS
        self.probleme.refresh_from_db()
        self.assertEqual(self.probleme.statut, "EN_COURS")
        
        # Check if an entry was created in HistoriqueModification for the probleme
        historique_probleme = HistoriqueModification.objects.filter(
            table_modifiee='Probleme',
            id_enregistrement=self.probleme.id,
            champ_modifie='statut',
            nouvelle_valeur='EN_COURS'
        ).first()
        
        self.assertIsNotNone(historique_probleme)
    
    def test_get_probleme_statistics(self):
        """Test getting probleme statistics"""
        # Create additional problemes for statistics
        Probleme.objects.create(
            projet=self.projet,
            titre="Problème 2",
            gravite="ELEVEE",
            statut="RESOLU",
            signale_par=self.utilisateur
        )
        
        Probleme.objects.create(
            projet=self.projet,
            titre="Problème 3",
            gravite="CRITIQUE",
            statut="FERME",
            signale_par=self.utilisateur
        )
        
        Probleme.objects.create(
            projet=self.projet,
            titre="Problème 4",
            gravite="MOYENNE",
            statut="EN_COURS",
            signale_par=self.utilisateur
        )
        
        # Test for all problemes
        stats = get_probleme_statistics()
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['par_statut']['OUVERT'], 1)
        self.assertEqual(stats['par_statut']['RESOLU'], 1)
        self.assertEqual(stats['par_statut']['FERME'], 1)
        self.assertEqual(stats['par_statut']['EN_COURS'], 1)
        self.assertEqual(stats['par_gravite']['MOYENNE'], 2)
        self.assertEqual(stats['taux_resolution'], 50)
        
        # Test for projet specific problemes
        stats_projet = get_probleme_statistics(projet_id=self.projet.id)
        self.assertEqual(stats_projet['total'], 4)
        self.assertEqual(stats_projet['taux_resolution'], 50)


class APIViewTests(APITestCase):
    def setUp(self):
        # Create test user
        self.utilisateur = Utilisateur.objects.create(
            email="test@example.com",
            nom="Doe",
            prenom="John",
            role="INGENIEUR_TERRAIN"
        )
        self.utilisateur.set_password("password123")
        self.utilisateur.save()
        
        # Set up API client and authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.utilisateur)
        
        # Create test data
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            responsable=self.utilisateur
        )
        
        self.phase = Phase.objects.create(
            projet=self.projet,
            nom="Phase Test",
            ordre=1,
            statut="EN_COURS"
        )
        
        self.operation = Operation.objects.create(
            phase=self.phase,
            nom="Operation Test",
            statut="EN_COURS"
        )
        
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
        
        self.solution = Solution.objects.create(
            probleme=self.probleme,
            description="Description de la solution test",
            type_solution="Correctif",
            cout_estime=Decimal("1000.00"),
            delai_estime=5,
            proposee_par=self.utilisateur
        )

    def test_probleme_list_view_get(self):
        """Test GET request to ProblemeListView"""
        url = reverse('probleme-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test with filters
        response = self.client.get(f"{url}?projet={self.projet.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        response = self.client.get(f"{url}?statut=RESOLU")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
    
    def test_probleme_list_view_post(self):
        """Test POST request to ProblemeListView"""
        url = reverse('probleme-list')
        data = {
            'titre': 'Nouveau Problème',
            'description': 'Description du nouveau problème',
            'gravite': 'ELEVEE',
            'projet': self.projet.id,
            'phase': self.phase.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titre'], 'Nouveau Problème')
        self.assertEqual(response.data['gravite'], 'ELEVEE')
        self.assertEqual(response.data['signale_par_nom'], 'John Doe')
        
        # Check that the probleme was created in the database
        self.assertEqual(Probleme.objects.count(), 2)
    
    def test_probleme_detail_view(self):
        """Test ProblemeDetailView"""
        url = reverse('probleme-detail', args=[self.probleme.id])
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titre'], 'Problème Test')
        self.assertEqual(len(response.data['solutions']), 1)
        
        # Test PATCH
        patch_data = {
            'titre': 'Problème Test Modifié',
            'statut': 'RESOLU'
        }
        
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titre'], 'Problème Test Modifié')
        self.assertEqual(response.data['statut'], 'RESOLU')
        
        # Check that resolu_par and date_resolution were updated
        self.assertEqual(response.data['resolu_par']['nom_complet'], 'John Doe')
        self.assertIsNotNone(response.data['date_resolution'])
        
        # Test DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Probleme.objects.count(), 0)
    
    def test_solution_list_view(self):
        """Test SolutionListView"""
        url = reverse('solution-list')
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test with filters
        response = self.client.get(f"{url}?probleme={self.probleme.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test POST
        data = {
            'probleme': self.probleme.id,
            'description': 'Nouvelle solution',
            'type_solution': 'Préventif',
            'cout_estime': '2000.00',
            'delai_estime': 10
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Nouvelle solution')
        self.assertEqual(response.data['proposee_par_nom'], 'John Doe')
        
        # Check that the solution was created in the database
        self.assertEqual(Solution.objects.count(), 2)
    
    def test_solution_detail_view(self):
        """Test SolutionDetailView"""
        url = reverse('solution-detail', args=[self.solution.id])
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Description de la solution test')
        
        # Test PATCH
        patch_data = {
            'description': 'Solution modifiée',
            'statut': 'VALIDEE'
        }
        
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Solution modifiée')
        self.assertEqual(response.data['statut'], 'VALIDEE')
        
        # Check that validee_par and date_validation were updated
        self.assertEqual(response.data['validee_par_nom'], 'John Doe')
        self.assertIsNotNone(response.data['date_validation'])
        
        # Test DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Solution.objects.count(), 0)
    
    def test_problemes_by_entity_view(self):
        """Test ProblemesByEntityView"""
        # Test with projet
        url = reverse('problemes-by-entity', args=['projet', self.projet.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test with phase
        url = reverse('problemes-by-entity', args=['phase', self.phase.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test with operation
        url = reverse('problemes-by-entity', args=['operation', self.operation.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test with invalid entity type
        url = reverse('problemes-by-entity', args=['invalid', 1])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_solutions_by_probleme_view(self):
        """Test SolutionsByProblemeView"""
        url = reverse('solutions-by-probleme', args=[self.probleme.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Description de la solution test')