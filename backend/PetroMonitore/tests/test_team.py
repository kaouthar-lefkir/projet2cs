from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from datetime import timedelta

from PetroMonitore.models import (
    Utilisateur, 
    Projet, 
    EquipeProjet, 
    HistoriqueModification
)


class EquipeProjetModelTests(TestCase):
    """Tests pour le modèle EquipeProjet."""
    
    def setUp(self):
        # Création d'utilisateurs pour les tests
        self.user1 = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            mot_de_passe="password123",
            role="INGENIEUR_TERRAIN",
            statut="ACTIF"
        )
        
        self.user2 = Utilisateur.objects.create(
            nom="Martin",
            prenom="Sophie",
            email="sophie.martin@example.com",
            mot_de_passe="password123",
            role="EXPERT",
            statut="ACTIF"
        )
        
        # Création d'un projet pour les tests
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            seuil_alerte_cout=80,
            seuil_alerte_delai=80
        )
    
    def test_create_equipe_projet(self):
        """Test de création d'une affectation d'équipe."""
        equipe = EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.user1,
            role_projet="Chef de Projet",
            affecte_par=self.user2
        )
        
        self.assertEqual(equipe.projet, self.projet)
        self.assertEqual(equipe.utilisateur, self.user1)
        self.assertEqual(equipe.role_projet, "Chef de Projet")
        self.assertEqual(equipe.affecte_par, self.user2)
        self.assertIsNotNone(equipe.date_affectation)
    
    def test_string_representation(self):
        """Test de la représentation textuelle du modèle."""
        equipe = EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.user1,
            role_projet="Chef de Projet",
            affecte_par=self.user2
        )
        
        expected_string = f"{self.user1.prenom} {self.user1.nom} - {self.projet.nom}"
        self.assertEqual(str(equipe), expected_string)
    
    def test_unique_together_constraint(self):
        """Test de la contrainte d'unicité (projet, utilisateur)."""
        # Création d'une première affectation
        EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.user1,
            role_projet="Chef de Projet",
            affecte_par=self.user2
        )
        
        # La création d'une seconde affectation pour le même utilisateur et projet devrait échouer
        with self.assertRaises(Exception):
            EquipeProjet.objects.create(
                projet=self.projet,
                utilisateur=self.user1,
                role_projet="Ingénieur",
                affecte_par=self.user2
            )


class EquipeProjetAPITests(APITestCase):
    """Tests pour les API de gestion d'équipe."""
    
    def setUp(self):
        # Création d'utilisateurs pour les tests
        self.user1 = Utilisateur.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com",
            role="INGENIEUR_TERRAIN",
            statut="ACTIF",
            is_staff=True
        )
        self.user1.set_password("password123")
        self.user1.save()
        
        self.user2 = Utilisateur.objects.create(
            nom="Martin",
            prenom="Sophie",
            email="sophie.martin@example.com",
            role="EXPERT",
            statut="ACTIF"
        )
        self.user2.set_password("password123")
        self.user2.save()
        
        # Création de projets pour les tests
        self.projet1 = Projet.objects.create(
            nom="Projet Test 1",
            description="Description du projet test 1",
            statut="EN_COURS",
            seuil_alerte_cout=80,
            seuil_alerte_delai=80
        )
        
        self.projet2 = Projet.objects.create(
            nom="Projet Test 2",
            description="Description du projet test 2",
            statut="PLANIFIE",
            seuil_alerte_cout=75,
            seuil_alerte_delai=75
        )
        
        # Création d'une affectation d'équipe pour les tests
        self.equipe = EquipeProjet.objects.create(
            projet=self.projet1,
            utilisateur=self.user2,
            role_projet="Chef de Projet",
            affecte_par=self.user1
        )
        
        # Authentification pour les tests API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
    
    def test_list_equipe_projet(self):
        """Test de récupération de la liste des affectations d'équipe."""
        url = reverse('equipe-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_equipe_projet(self):
        """Test de création d'une affectation d'équipe via API."""
        url = reverse('equipe-list-create')
        data = {
            'projet': self.projet2.id,
            'utilisateur': self.user2.id,
            'role_projet': 'Ingénieur'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EquipeProjet.objects.count(), 2)
        self.assertEqual(response.data['role_projet'], 'Ingénieur')
        
        # Vérification de l'enregistrement dans l'historique
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='creation'
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertEqual(historique.modifie_par, self.user1)
    
    def test_retrieve_equipe_projet(self):
        """Test de récupération d'une affectation d'équipe spécifique."""
        url = reverse('equipe-detail', args=[self.equipe.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.equipe.id)
        self.assertEqual(response.data['role_projet'], 'Chef de Projet')
    
    def test_update_equipe_projet(self):
        """Test de mise à jour d'une affectation d'équipe."""
        url = reverse('equipe-detail', args=[self.equipe.id])
        data = {'role_projet': 'Responsable Technique'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.equipe.refresh_from_db()
        self.assertEqual(self.equipe.role_projet, 'Responsable Technique')
        
        # Vérification de l'enregistrement dans l'historique
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='role_projet'
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertEqual(historique.ancienne_valeur, 'Chef de Projet')
        self.assertEqual(historique.nouvelle_valeur, 'Responsable Technique')
    
    def test_delete_equipe_projet(self):
        """Test de suppression d'une affectation d'équipe."""
        url = reverse('equipe-detail', args=[self.equipe.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EquipeProjet.objects.count(), 0)
        
        # Vérification de l'enregistrement dans l'historique
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='suppression'
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertTrue(str(self.equipe.utilisateur.id) in historique.ancienne_valeur)
    
    def test_filter_by_projet(self):
        """Test du filtrage des affectations par projet."""
        # Création d'une seconde affectation
        EquipeProjet.objects.create(
            projet=self.projet2,
            utilisateur=self.user1,
            role_projet="Développeur",
            affecte_par=self.user1
        )
        
        url = reverse('equipe-list-create')
        response = self.client.get(f"{url}?projet={self.projet1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['projet'], self.projet1.id)
    
    def test_filter_by_utilisateur(self):
        """Test du filtrage des affectations par utilisateur."""
        # Création d'une seconde affectation
        EquipeProjet.objects.create(
            projet=self.projet2,
            utilisateur=self.user1,
            role_projet="Développeur",
            affecte_par=self.user1
        )
        
        url = reverse('equipe-list-create')
        response = self.client.get(f"{url}?utilisateur={self.user2.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['utilisateur'], self.user2.id)
    
    def test_projet_membres(self):
        """Test de récupération des membres d'un projet spécifique."""
        # Création d'une seconde affectation pour le même projet
        EquipeProjet.objects.create(
            projet=self.projet1,
            utilisateur=self.user1,
            role_projet="Développeur",
            affecte_par=self.user1
        )
        
        url = reverse('projet-membres', args=[self.projet1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Vérification que les données détaillées des utilisateurs sont incluses
        self.assertIn('utilisateur', response.data[0])
        self.assertIn('nom', response.data[0]['utilisateur'])
        self.assertIn('prenom', response.data[0]['utilisateur'])
    
    def test_affecter_utilisateur(self):
        """Test d'affectation d'un utilisateur à un projet via l'endpoint dédié."""
        url = reverse('affecter-utilisateur')
        data = {
            'projet_id': self.projet2.id,
            'utilisateur_id': self.user1.id,
            'role_projet': 'Analyste'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EquipeProjet.objects.count(), 2)
        
        # Vérification de l'existence de l'affectation
        affectation = EquipeProjet.objects.filter(
            projet=self.projet2,
            utilisateur=self.user1
        ).first()
        
        self.assertIsNotNone(affectation)
        self.assertEqual(affectation.role_projet, 'Analyste')
    
    def test_affecter_utilisateur_already_exists(self):
        """Test d'affectation d'un utilisateur déjà affecté au même projet."""
        url = reverse('affecter-utilisateur')
        data = {
            'projet_id': self.projet1.id,
            'utilisateur_id': self.user2.id,
            'role_projet': 'Autre Rôle'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_desaffecter_utilisateur(self):
        """Test de désaffectation d'un utilisateur d'un projet."""
        url = reverse('desaffecter-utilisateur', args=[self.equipe.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EquipeProjet.objects.count(), 0)
        
        # Vérification de l'enregistrement dans l'historique
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='suppression'
        ).first()
        
        self.assertIsNotNone(historique)