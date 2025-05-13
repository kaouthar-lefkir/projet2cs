from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from PetroMonitore.models import Projet, Utilisateur, Phase, Operation, EquipeProjet
from PetroMonitore.serializers import ProjetSerializer, ProjetDetailSerializer
from PetroMonitore.utils import (
    get_tokens_for_user, 
    update_project_costs, 
    update_phase_costs, 
    calculate_project_progress
)

class ProjetManagementTestCase(TestCase):
    def setUp(self):
        """
        Configuration initiale pour les tests
        """
        # Création des utilisateurs avec différents rôles
        self.top_management = Utilisateur.objects.create(
            email='top@example.com', 
            nom='Management', 
            prenom='Top', 
            role='TOP_MANAGEMENT', 
            statut='ACTIF',
            mot_de_passe='testpassword123'
        )
        
        self.expert = Utilisateur.objects.create(
            email='expert@example.com', 
            nom='Expert', 
            prenom='Project', 
            role='EXPERT', 
            statut='ACTIF',
            mot_de_passe='testpassword123'
        )
        
        self.ingenieur_terrain = Utilisateur.objects.create(
            email='ingenieur@example.com', 
            nom='Terrain', 
            prenom='Ingenieur', 
            role='INGENIEUR_TERRAIN', 
            statut='ACTIF',
            mot_de_passe='testpassword123'
        )
        
        # Création d'un projet de base
        self.projet = Projet.objects.create(
            nom='Projet Test',
            description='Description du projet de test',
            localisation='Paris',
            budget_initial=Decimal('100000.00'),
            date_debut=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=90),
            statut='EN_COURS',
            responsable=self.expert,
            seuil_alerte_cout=Decimal('80'),
            seuil_alerte_delai=Decimal('80')
        )
        
        # Affecter les membres de l'équipe
        EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.top_management,
            role_projet='Superviseur'
        )
        EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.expert,
            role_projet='Responsable de Projet'
        )
        
        # Création d'un client API pour les tests
        self.client = APIClient()
        
        # Générer des tokens pour les utilisateurs
        self.top_management_token = get_tokens_for_user(self.top_management)
        self.expert_token = get_tokens_for_user(self.expert)
        self.ingenieur_terrain_token = get_tokens_for_user(self.ingenieur_terrain)

    def authenticate(self, user_token):
        """
        Authentifie le client avec un token donné
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token["access"]}')

    def test_project_cost_update_functions(self):
        """
        Test les fonctions de mise à jour des coûts de projet
        """
        # Création d'une phase avec des opérations
        phase = Phase.objects.create(
            projet=self.projet,
            nom='Phase Test',
            budget_alloue=Decimal('20000.00'),
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=30),
            statut='EN_COURS',
            ordre=1  # Ajout de l'ordre requis
        )
        
        # Création d'opérations
        Operation.objects.create(
            phase=phase,
            nom='Opération 1',
            cout_reel=Decimal('5000.00'),
            statut='TERMINE',
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=10)
        )
        Operation.objects.create(
            phase=phase,
            nom='Opération 2',
            cout_reel=Decimal('7500.00'),
            statut='EN_COURS',
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=15)
        )
        
        # Test de mise à jour des coûts de phase
        result = update_phase_costs(phase.id)
        self.assertTrue(result)
        
        # Vérifier que le coût de la phase a été mis à jour
        phase.refresh_from_db()
        self.assertEqual(phase.cout_actuel, Decimal('12500.00'))
        
        # Vérifier que le coût du projet a été mis à jour
        self.projet.refresh_from_db()
        self.assertEqual(self.projet.cout_actuel, Decimal('12500.00'))

    def test_project_progress_calculation(self):
        """
        Test le calcul de la progression d'un projet
        """
        # Création de phases avec différentes progressions
        Phase.objects.create(
            projet=self.projet,
            nom='Phase 1',
            progression=Decimal('50.00'),
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=30),
            statut='EN_COURS',
            ordre=1  # Ajout de l'ordre requis
        )
        Phase.objects.create(
            projet=self.projet,
            nom='Phase 2',
            progression=Decimal('75.00'),
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=30),
            statut='EN_COURS',
            ordre=2  # Ajout de l'ordre requis
        )
        
        # Calculer la progression du projet
        progress = calculate_project_progress(self.projet.id)
        
        # Vérifier que la progression est correcte
        # (50 + 75) / 2 = 62.5
        self.assertEqual(progress, Decimal('62.50'))

    # Les autres méthodes de test restent les mêmes que dans la version précédente