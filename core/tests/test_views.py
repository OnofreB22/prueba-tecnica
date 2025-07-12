from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User, UserAction
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewsTest(APITestCase):
    """Tests para las vistas de registro, login, logout y acciones de usuario"""

    def setUp(self):
        """Crea un usuario de prueba para los tests"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_user_register_view(self):
        """Testea el registro de usuario y el registro de la accion signup"""
        url = reverse('user_register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        self.assertTrue(UserAction.objects.filter(user__email='newuser@example.com', action='signup').exists())

    def test_login_view_and_action(self):
        """Testea el login y el registro de la accion login"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue(UserAction.objects.filter(user=self.user, action='login').exists())

    def test_logout_view_and_action(self):
        """Testea el logout y el registro de la accion logout"""
        # Login para obtener tokens
        login_url = reverse('token_obtain_pair')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Logout
        logout_url = reverse('logout')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.post(logout_url, {'refresh': refresh_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertTrue(UserAction.objects.filter(user=self.user, action='logout').exists())

    def test_user_action_list_view(self):
        """Testea la consulta del historial de acciones del usuario autenticado"""
        # Crear acciones
        UserAction.objects.create(user=self.user, action='signup')
        UserAction.objects.create(user=self.user, action='login')

        # Login para obtener token
        url = reverse('token_obtain_pair')
        data = {'email': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post(url, data)
        access_token = response.data['access']

        # Consultar historial
        actions_url = reverse('user_actions')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(actions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
