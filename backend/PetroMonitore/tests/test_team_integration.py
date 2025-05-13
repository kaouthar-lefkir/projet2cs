from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from datetime import timedelta

from PetroMonitore.models import (
    Utilisateur,
    Projet,
    Phase,
    Operation,
    EquipeProjet,
    HistoriqueModification
)


class EquipeProjetIntegrationTests(APITestCase):
    """Tests d'intégration pour les fonctionnalités de gestion d'équipe."""
    
    def setUp(self):
        # Création d'utilisateurs pour les tests
        self.manager = Utilisateur.objects.create(
            nom="Dubois",
            prenom="Pierre",
            email="pierre.dubois@example.com",
            role="TOP_MANAGEMENT",
            statut="ACTIF",
            is_staff=True
        )
        self.manager.set_password("password123")
        self.manager.save()
        
        self.ingenieur1 = Utilisateur.objects.create(
            nom="Robert",
            prenom="Marie",
            email="marie.robert@example.com",
            role="INGENIEUR_TERRAIN",
            statut="ACTIF"
        )
        self.ingenieur1.set_password("password123")
        self.ingenieur1.save()
        
        self.ingenieur2 = Utilisateur.objects.create(
            nom="Moreau",
            prenom="Thomas",
            email="thomas.moreau@example.com",
            role="INGENIEUR_TERRAIN",
            statut="ACTIF"
        )
        self.ingenieur2.set_password("password123")
        self.ingenieur2.save()
        
        self.expert = Utilisateur.objects.create(
            nom="Petit",
            prenom="Emilie",
            email="emilie.petit@example.com",
            role="EXPERT",
            statut="ACTIF"
        )
        self.expert.set_password("password123")
        self.expert.save()
        
        # Création d'un projet complexe pour les tests
        self.projet = Projet.objects.create(
            nom="Construction Bâtiment A",
            description="Construction d'un nouveau bâtiment administratif",
            localisation="Paris",
            budget_initial=1000000.00,
            cout_actuel=0.00,
            date_debut=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=365),
            statut="EN_COURS",
            responsable=self.manager,
            seuil_alerte_cout=85,
            seuil_alerte_delai=80
        )
        
        # Création de quelques phases
        self.phase1 = Phase.objects.create(
            projet=self.projet,
            nom="Études préliminaires",
            description="Études de faisabilité et conception préliminaire",
            ordre=1,
            date_debut_prevue=timezone.now().date(),
            date_fin_prevue=timezone.now().date() + timedelta(days=90),
            budget_alloue=100000.00,
            cout_actuel=0.00,
            progression=0.00,
            statut="PLANIFIE"
        )
        
        self.phase2 = Phase.objects.create(
            projet=self.projet,
            nom="Construction des fondations",
            description="Travaux de fondation et sous-sol",
            ordre=2,
            date_debut_prevue=timezone.now().date() + timedelta(days=91),
            date_fin_prevue=timezone.now().date() + timedelta(days=180),
            budget_alloue=250000.00,
            cout_actuel=0.00,
            progression=0.00,
            statut="PLANIFIE"
        )
        
        # Authentification pour les tests API
        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)
    
    def test_scenario_complet_gestion_equipe(self):
        """Test d'un scénario complet de gestion d'équipe pour un projet."""
        
        # 1. Affectation des membres de l'équipe au projet
        url_affecter = reverse('affecter-utilisateur')
        
        # Affecter l'ingénieur 1 comme chef de projet
        response = self.client.post(url_affecter, {
            'projet_id': self.projet.id,
            'utilisateur_id': self.ingenieur1.id,
            'role_projet': 'Chef de Projet'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Affecter l'ingénieur 2 comme responsable technique
        response = self.client.post(url_affecter, {
            'projet_id': self.projet.id,
            'utilisateur_id': self.ingenieur2.id,
            'role_projet': 'Responsable Technique'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Affecter l'expert comme consultant
        response = self.client.post(url_affecter, {
            'projet_id': self.projet.id,
            'utilisateur_id': self.expert.id,
            'role_projet': 'Consultant Expert'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Vérifier la liste des membres du projet
        url_membres = reverse('projet-membres', args=[self.projet.id])
        response = self.client.get(url_membres)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Vérifier les rôles
        roles = [membre['role_projet'] for membre in response.data]
        self.assertIn('Chef de Projet', roles)
        self.assertIn('Responsable Technique', roles)
        self.assertIn('Consultant Expert', roles)
        
        # 3. Modifier le rôle d'un membre
        chef_projet_id = None
        for membre in response.data:
            if membre['role_projet'] == 'Chef de Projet':
                chef_projet_id = membre['id']
                break
                
        self.assertIsNotNone(chef_projet_id)
        
        url_update = reverse('equipe-detail', args=[chef_projet_id])
        response = self.client.patch(url_update, {
            'role_projet': 'Directeur de Projet'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role_projet'], 'Directeur de Projet')
        
        # 4. Vérifier l'historique des modifications
        # Pour le rôle modifié
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='role_projet',
            ancienne_valeur='Chef de Projet'
        ).first()
        
        self.assertIsNotNone(historique)
        self.assertEqual(historique.nouvelle_valeur, 'Directeur de Projet')
        
        # 5. Désaffecter un membre
        # Refaire une requête pour obtenir la liste mise à jour des membres
        response = self.client.get(url_membres)
        
        # Chercher l'expert parmi les membres
        expert_id = None
        for membre in response.data:
            # Vérifier d'abord si role_projet existe et est accessible
            if isinstance(membre, dict) and 'role_projet' in membre:
                if membre['role_projet'] == 'Consultant Expert':
                    expert_id = membre['id']
                    break
        
        # Si on n'a pas trouvé l'expert, essayer une autre stratégie
        if expert_id is None:
            # Vérifier le format de la réponse pour comprendre sa structure
            print(f"Structure de la réponse pour debug: {type(response.data)}")
            if response.data and len(response.data) > 0:
                print(f"Premier élément: {type(response.data[0])}")
                if isinstance(response.data[0], dict):
                    print(f"Clés disponibles: {response.data[0].keys()}")
            
            # Chercher par l'email de l'utilisateur
            for membre in response.data:
                if isinstance(membre, dict) and 'utilisateur' in membre and isinstance(membre['utilisateur'], dict):
                    if membre['utilisateur'].get('email') == self.expert.email:
                        expert_id = membre['id']
                        break
        
        # S'assurer qu'on a trouvé l'ID de l'expert
        self.assertIsNotNone(expert_id, "Impossible de trouver l'ID de l'expert dans la réponse")
        
        # Maintenant désaffecter l'expert
        url_desaffecter = reverse('desaffecter-utilisateur', args=[expert_id])
        response = self.client.delete(url_desaffecter)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Vérifier que le membre a bien été désaffecté
        response = self.client.get(url_membres)
        self.assertEqual(len(response.data), 2)
        
        # Vérifier que l'expert n'est plus dans la liste
        emails = []
        for membre in response.data:
            if isinstance(membre, dict) and 'utilisateur' in membre and isinstance(membre['utilisateur'], dict):
                if 'email' in membre['utilisateur']:
                    emails.append(membre['utilisateur']['email'])
        
        self.assertNotIn(self.expert.email, emails)
        
        # 7. Vérifier l'historique de désaffectation
        historique = HistoriqueModification.objects.filter(
            table_modifiee='EquipeProjet',
            champ_modifie='suppression'
        ).first()
        
        self.assertIsNotNone(historique)
        # Vérifier que l'id de l'expert est mentionné dans l'ancienne valeur
        self.assertTrue(str(self.expert.id) in historique.ancienne_valeur)

    def test_filtrage_avance_equipe(self):
        """Test des fonctionnalités de filtrage avancé des membres d'équipe."""
        
        # Affecter plusieurs utilisateurs à différents projets
        # Créer un second projet
        projet2 = Projet.objects.create(
            nom="Rénovation Site B",
            description="Travaux de rénovation du site industriel B",
            statut="EN_COURS",
            responsable=self.manager
        )
        
        # Affecter les utilisateurs au premier projet
        EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.ingenieur1,
            role_projet="Chef de Projet",
            affecte_par=self.manager
        )
        
        EquipeProjet.objects.create(
            projet=self.projet,
            utilisateur=self.expert,
            role_projet="Consultant",
            affecte_par=self.manager
        )
        
        # Affecter des utilisateurs au second projet
        EquipeProjet.objects.create(
            projet=projet2,
            utilisateur=self.ingenieur2,
            role_projet="Chef de Projet",
            affecte_par=self.manager
        )
        
        EquipeProjet.objects.create(
            projet=projet2,
            utilisateur=self.ingenieur1,
            role_projet="Ingénieur Support",
            affecte_par=self.manager
        )
        
        # Tester le filtrage par projet
        url = reverse('equipe-list-create')
        response = self.client.get(f"{url}?projet={self.projet.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Tester le filtrage par utilisateur
        response = self.client.get(f"{url}?utilisateur={self.ingenieur1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # L'ingénieur1 est sur les deux projets
        
        # Tester le filtrage par rôle
        response = self.client.get(f"{url}?role=Chef")  # Recherche partielle
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Deux "Chef de Projet"
        
        # Tester la combinaison de filtres
        response = self.client.get(f"{url}?projet={self.projet.id}&role=Chef")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Un seul chef de projet dans le projet 1