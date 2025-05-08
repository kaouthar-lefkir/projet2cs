from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.hashers import make_password
from PetroMonitore.models import Utilisateur
from PetroMonitore.utils import get_tokens_for_user


class ProtectedViewsTest(APITestCase):

    def setUp(self):
        # Create a top management user (admin equivalent)
        self.admin = Utilisateur.objects.create(
            email='admin@example.com',
            nom='Admin',
            prenom='User',
            mot_de_passe=make_password('adminpass'),
            role='TOP_MANAGEMENT',  # Changed from ADMIN to TOP_MANAGEMENT
            statut='ACTIF',
            is_staff=True
        )
        
        # Regular user
        self.user = Utilisateur.objects.create(
            email='user@example.com',
            nom='Regular',
            prenom='User',
            mot_de_passe=make_password('userpass'),
            role='INGENIEUR_TERRAIN',
            statut='ACTIF'
        )

        self.client = APIClient()

    def authenticate_as(self, user):
        tokens = get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    def test_user_list_requires_admin(self):
        # Using reverse() to get the URL with the correct namespace
        url = reverse('user-list')  # This resolves to /api/users/
        
        self.authenticate_as(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate_as(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        self.authenticate_as(self.admin)
        url = reverse('user-list')  # Assuming you have this URL name
        data = {
            'email': 'newuser@example.com',
            'nom': 'New',
            'prenom': 'User',  # Required field as per your model
            'mot_de_passe': 'testpass123',
            'role': 'EXPERT',
            'statut': 'ACTIF'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_detail(self):
        self.authenticate_as(self.user)
        url = reverse('user-detail', args=[self.user.id])  # Assuming you have this URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        other_user = Utilisateur.objects.create(
            email='other@example.com',
            nom='Other',
            prenom='User',
            mot_de_passe=make_password('otherpass'),
            role='EXPERT',
            statut='ACTIF'
        )
        url = reverse('user-detail', args=[other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_detail(self):
        self.authenticate_as(self.user)
        url = reverse('user-detail', args=[self.user.id])
        data = {
            'email': self.user.email,  # Including existing email
            'nom': 'Updated',
            'prenom': 'Name',
            'role': 'EXPERT',
            'statut': 'ACTIF'  # Including status
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_requires_top_management(self):
        top = Utilisateur.objects.create(
            email='top@example.com',
            nom='Top',
            prenom='Manager',
            mot_de_passe=make_password('top'),
            role='TOP_MANAGEMENT',
            statut='ACTIF'
        )
        user_to_delete = Utilisateur.objects.create(
            email='todelete@example.com',
            nom='Delete',
            prenom='User',
            mot_de_passe=make_password('deletepass'),
            role='EXPERT',
            statut='ACTIF'
        )

        self.authenticate_as(self.user)
        url = reverse('user-detail', args=[user_to_delete.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate_as(top)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password(self):
        self.authenticate_as(self.user)
        url = reverse('change-password')  # Assuming you have this URL name
        data = {
            'old_password': 'userpass',
            'new_password': 'newsecurepass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_profile_view(self):
        self.authenticate_as(self.user)
        url = reverse('profile')  # Assuming you have this URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)