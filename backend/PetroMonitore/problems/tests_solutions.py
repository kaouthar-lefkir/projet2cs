from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
import json

from ..models import Solution, Probleme, Projet, Utilisateur
from .solution_utils import get_solution_statistics, get_solutions_to_implement

class SolutionViewsTestCase(TestCase):
    def setUp(self):
        # Créer un utilisateur pour l'authentification
        self.user = Utilisateur.objects.create(
            nom="User",
            prenom="Test",
            email="test@example.com",
            role="EXPERT",
            statut="ACTIF"
        )
        self.user.set_password("testpassword")
        self.user.save()
        
        # Créer un client API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            date_creation=timezone.now(),
            responsable=self.user
        )
        
        # Créer un problème
        self.probleme = Probleme.objects.create(
            titre="Problème Test",
            description="Description du problème test",
            statut="EN_COURS",
            gravite="MOYENNE",
            projet=self.projet,
            signale_par=self.user
        )
        
        # Créer quelques solutions avec différents statuts
        self.solution_proposee = Solution.objects.create(
            description="Solution proposée",
            statut="PROPOSEE",
            type_solution="TECHNIQUE",
            cout_estime=1000.0,
            delai_estime=30,
            probleme=self.probleme,
            proposee_par=self.user
        )
        
        self.solution_validee = Solution.objects.create(
            description="Solution validée",
            statut="VALIDEE",
            type_solution="ORGANISATIONNELLE",
            cout_estime=2000.0,
            delai_estime=60,
            probleme=self.probleme,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
        
        self.solution_rejetee = Solution.objects.create(
            description="Solution rejetée",
            statut="REJETEE",
            type_solution="TECHNIQUE",
            cout_estime=3000.0,
            delai_estime=90,
            probleme=self.probleme,
            proposee_par=self.user
        )
        
        self.solution_mise_en_oeuvre = Solution.objects.create(
            description="Solution mise en œuvre",
            statut="MISE_EN_OEUVRE",
            type_solution="TECHNIQUE",
            cout_estime=1500.0,
            delai_estime=45,
            probleme=self.probleme,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
        
        # Créer un second projet avec son propre problème et solution
        self.projet2 = Projet.objects.create(
            nom="Projet 2",
            description="Description du projet 2",
            statut="EN_COURS",
            date_creation=timezone.now(),
            responsable=self.user
        )
        
        self.probleme2 = Probleme.objects.create(
            titre="Problème 2",
            description="Description du problème 2",
            statut="EN_COURS",
            gravite="ELEVEE",
            projet=self.projet2,
            signale_par=self.user
        )
        
        self.solution_projet2 = Solution.objects.create(
            description="Solution du projet 2",
            statut="VALIDEE",
            type_solution="TECHNIQUE",
            cout_estime=2500.0,
            delai_estime=75,
            probleme=self.probleme2,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
    
    def test_solution_statistics_view(self):
        """Tester la vue de statistiques des solutions"""
        # Tester sans filtre
        url = reverse('solution-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le contenu de la réponse
        data = response.json()
        self.assertEqual(data['total'], 5)  # 5 solutions au total
        self.assertEqual(data['par_statut']['VALIDEE'], 2)  # 2 solutions validées
        self.assertEqual(data['par_statut']['MISE_EN_OEUVRE'], 1)  # 1 solution mise en œuvre
        
        # Vérifier les statistiques de coût et délai
        self.assertIn('cout', data)
        self.assertIn('delai', data)
        
        # Tester avec filtre par problème
        url = f"{reverse('solution-statistics')}?probleme={self.probleme.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total'], 4)  # 4 solutions pour ce problème
        
        # Tester avec filtre par projet
        url = f"{reverse('solution-statistics')}?projet={self.projet.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total'], 4)  # 4 solutions pour ce projet
    
    def test_solutions_advanced_filter_view(self):
        """Tester la vue de filtrage avancé des solutions"""
        url = reverse('solution-advanced-filter')
        
        # Test sans filtre (toutes les solutions)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 5)  # 5 solutions au total
        
        # Test avec filtre par problème
        response = self.client.get(f"{url}?probleme={self.probleme.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 4)  # 4 solutions pour ce problème
        
        # Test avec filtre par statut
        response = self.client.get(f"{url}?statut=VALIDEE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)  # 2 solutions validées
        
        # Test avec filtre par type de solution
        response = self.client.get(f"{url}?type=TECHNIQUE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 4)  # 4 solutions techniques
        
        # Test avec filtre sur le coût
        response = self.client.get(f"{url}?cout_min=1500&cout_max=2500")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 3)  # 3 solutions entre 1500 et 2500
        
        # Test avec filtre sur le délai
        response = self.client.get(f"{url}?delai_min=40&delai_max=80")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 3)  # 3 solutions avec délai entre 40 et 80
        
        # Test de recherche textuelle
        response = self.client.get(f"{url}?search=rejetée")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution contient "rejetée"
        
        # Test combinaison de filtres
        response = self.client.get(f"{url}?statut=VALIDEE&type=TECHNIQUE&cout_min=2000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution correspond à tous ces critères
    
    def test_solutions_to_implement_view(self):
        """Tester la vue des solutions à mettre en œuvre"""
        url = reverse('solutions-to-implement')
        
        # Test sans filtre (toutes les solutions validées)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)  # 2 solutions validées
        
        # Test avec filtre par projet
        response = self.client.get(f"{url}?projet={self.projet.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution validée pour ce projet
        
        # Vérifier que la solution du projet 2 est correctement filtrée
        response = self.client.get(f"{url}?projet={self.projet2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution validée pour le projet 2
        
        # Vérifier que les solutions mises en œuvre ne sont pas incluses
        for solution in data['results']:
            self.assertEqual(solution['statut'], 'VALIDEE')
    
    def test_solution_mise_en_oeuvre_view(self):
        """Tester la vue de mise en œuvre d'une solution"""
        url = reverse('solution-implement', kwargs={'pk': self.solution_validee.id})
        
        # Tester la mise en œuvre d'une solution validée
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le statut a été mis à jour
        solution_updated = Solution.objects.get(pk=self.solution_validee.id)
        self.assertEqual(solution_updated.statut, 'MISE_EN_OEUVRE')
        
        # Tester avec une solution déjà mise en œuvre
        url = reverse('solution-implement', kwargs={'pk': self.solution_mise_en_oeuvre.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Tester avec une solution rejetée
        url = reverse('solution-implement', kwargs={'pk': self.solution_rejetee.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_solutions_by_projet_view(self):
        """Tester la vue des solutions par projet"""
        url = reverse('solutions-by-projet', kwargs={'projet_id': self.projet.id})
        
        # Test sans filtre (toutes les solutions du projet)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 4)  # 4 solutions pour ce projet
        
        # Test avec filtre par statut
        response = self.client.get(f"{url}?statut=VALIDEE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution validée pour ce projet
        
        # Test avec un projet inexistant
        url = reverse('solutions-by-projet', kwargs={'projet_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Vérifier que les solutions du projet 2 ne sont pas mélangées
        url = reverse('solutions-by-projet', kwargs={'projet_id': self.projet2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)  # 1 solution pour le projet 2

class SolutionUtilsTestCase(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = Utilisateur.objects.create(
            nom="User",
            prenom="Test",
            email="test@example.com",
            role="EXPERT",
            statut="ACTIF"
        )
        self.user.set_password("testpassword")
        self.user.save()
        
        # Créer un projet
        self.projet = Projet.objects.create(
            nom="Projet Test",
            description="Description du projet test",
            statut="EN_COURS",
            date_creation=timezone.now(),
            responsable=self.user
        )
        
        # Créer un problème
        self.probleme = Probleme.objects.create(
            titre="Problème Test",
            description="Description du problème test",
            statut="EN_COURS",
            gravite="MOYENNE",
            projet=self.projet,
            signale_par=self.user
        )
        
        # Créer des solutions avec différents statuts
        Solution.objects.create(
            description="Solution 1",
            statut="PROPOSEE",
            type_solution="TECHNIQUE",
            cout_estime=1000.0,
            delai_estime=30,
            probleme=self.probleme,
            proposee_par=self.user
        )
        
        Solution.objects.create(
            description="Solution 2",
            statut="VALIDEE",
            type_solution="ORGANISATIONNELLE",
            cout_estime=2000.0,
            delai_estime=60,
            probleme=self.probleme,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
        
        Solution.objects.create(
            description="Solution 3",
            statut="REJETEE",
            type_solution="TECHNIQUE",
            cout_estime=3000.0,
            delai_estime=90,
            probleme=self.probleme,
            proposee_par=self.user
        )
        
        Solution.objects.create(
            description="Solution 4",
            statut="MISE_EN_OEUVRE",
            type_solution="TECHNIQUE",
            cout_estime=1500.0,
            delai_estime=45,
            probleme=self.probleme,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
        
        # Créer un second problème avec une solution
        self.probleme2 = Probleme.objects.create(
            titre="Problème 2",
            description="Description du problème 2",
            statut="EN_COURS",
            gravite="ELEVEE",
            projet=self.projet,
            signale_par=self.user
        )
        
        Solution.objects.create(
            description="Solution 5",
            statut="VALIDEE",
            type_solution="TECHNIQUE",
            cout_estime=2500.0,
            delai_estime=75,
            probleme=self.probleme2,
            proposee_par=self.user,
            validee_par=self.user,
            date_validation=timezone.now()
        )
    
    def test_get_solution_statistics(self):
        """Tester la fonction get_solution_statistics"""
        # Test sans filtre
        stats = get_solution_statistics()
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['par_statut']['PROPOSEE'], 1)
        self.assertEqual(stats['par_statut']['VALIDEE'], 2)
        self.assertEqual(stats['par_statut']['REJETEE'], 1)
        self.assertEqual(stats['par_statut']['MISE_EN_OEUVRE'], 1)
        
        # Test avec filtre par problème
        stats = get_solution_statistics(probleme_id=self.probleme.id)
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['par_statut']['VALIDEE'], 1)
        
        # Test avec filtre par projet
        stats = get_solution_statistics(projet_id=self.projet.id)
        self.assertEqual(stats['total'], 5)
        
        # Vérifier les calculs de taux
        # Taux de validation = (validées + mises en œuvre) / total
        expected_taux_validation = ((2 + 1) / 5) * 100
        self.assertEqual(stats['taux_validation'], round(expected_taux_validation, 2))
        
        # Taux de mise en œuvre = mises en œuvre / (validées + mises en œuvre)
        expected_taux_mise_en_oeuvre = (1 / (2 + 1)) * 100
        self.assertEqual(stats['taux_mise_en_oeuvre'], round(expected_taux_mise_en_oeuvre, 2))
    
    def test_get_solutions_to_implement(self):
        """Tester la fonction get_solutions_to_implement"""
        # Test sans filtre
        solutions = get_solutions_to_implement()
        self.assertEqual(solutions.count(), 2)
        
        # Vérifier que toutes les solutions sont bien VALIDEE
        for solution in solutions:
            self.assertEqual(solution.statut, 'VALIDEE')
        
        # Test avec filtre par projet
        solutions = get_solutions_to_implement(projet_id=self.projet.id)
        self.assertEqual(solutions.count(), 2)

# Définir une fonction mock pour le test de track_solution_status_change
# Cette fonction serait normalement dans utils.py mais nous la simulons ici
def track_solution_status_change(solution_id, old_status, new_status, user):
    """
    Mock de la fonction pour traquer les changements de statut des solutions
    """
    # Dans un test réel, nous nous assurerions que cette fonction est appelée avec les bons arguments
    pass

# Ajouter cette fonction au module pour qu'elle soit accessible pendant les tests
from unittest.mock import patch
import sys
sys.modules['.utils'] = type('MockModule', (), {'track_solution_status_change': track_solution_status_change})