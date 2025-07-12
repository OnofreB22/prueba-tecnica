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

    def test_user_action_list_view_two_users(self):
        """
        Testea que el endpoint de acciones solo devuelve el historial del usuario autenticado,
        incluso si hay acciones de otros usuarios en la base de datos.
        """
        # Crear segundo usuario
        user2 = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='otherpass123'
        )
        
        # Contar acciones existentes
        initial_user1_actions = UserAction.objects.filter(user=self.user).count()
        initial_user2_actions = UserAction.objects.filter(user=user2).count()
        
        # Crear acciones para ambos usuarios
        UserAction.objects.create(user=self.user, action='signup')
        UserAction.objects.create(user=self.user, action='login')
        UserAction.objects.create(user=user2, action='signup')
        UserAction.objects.create(user=user2, action='logout')
        
        # Login como self.user
        url = reverse('token_obtain_pair')
        data = {'email': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post(url, data)
        access_token = response.data['access']
        
        # Consultar historial de acciones como self.user
        actions_url = reverse('user_actions')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(actions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actions = response.data
        
        # Verificar que aparecen las acciones esperadas de self.user
        expected_actions = ['signup', 'login']
        returned_actions = [a['action'] for a in actions]
        
        # Verificar que las nuevas acciones estan presentes
        for expected_action in expected_actions:
            self.assertIn(expected_action, returned_actions)
        
        # Verificar que hay al menos 2 acciones mas que al inicio
        self.assertGreaterEqual(len(actions), initial_user1_actions + 2)
        
        # Verificar que solo contiene los campos esperados
        for action in actions:
            self.assertIn('action', action)
            self.assertIn('timestamp', action)
            self.assertEqual(len(action), 2)
        
        # Login como user2
        response2 = self.client.post(url, {'email': 'other@example.com', 'password': 'otherpass123'})
        access_token2 = response2.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')
        response = self.client.get(actions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actions = response.data
        
        # Verificar que aparecen las acciones de user2
        expected_actions_user2 = ['signup', 'logout']
        returned_actions_user2 = [a['action'] for a in actions]
        
        # Verificar que las nuevas acciones estan presentes
        for expected_action in expected_actions_user2:
            self.assertIn(expected_action, returned_actions_user2)
        
        # Verificar que hay al menos 2 acciones mas que al inicio
        self.assertGreaterEqual(len(actions), initial_user2_actions + 2)
