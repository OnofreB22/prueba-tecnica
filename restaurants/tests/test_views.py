from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User, UserAction
from unittest.mock import patch

class NearbyRestaurantsViewTest(APITestCase):
    """Tests para la vista NearbyRestaurantsView."""

    def setUp(self):
        """Crea un usuario y obtiene su token de acceso"""
        self.user = User.objects.create_user(
            email='testrest@example.com',
            username='testrest',
            password='testpass123'
        )

        url = reverse('token_obtain_pair')
        resp = self.client.post(url, {'email': 'testrest@example.com', 'password': 'testpass123'})

        self.access_token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.url = reverse('nearby_restaurants')

    @patch('restaurants.views.requests.get')
    def test_search_by_city(self, mock_get):
        """Testea busqueda de restaurantes usando ciudad"""

        # Mock respuesta
        mock_get.side_effect = [
            # Geocoding API response
            type('obj', (object,), {'json': lambda s: {
                'status': 'OK',
                'results': [{'geometry': {'location': {'lat': 6.2442, 'lng': -75.5812}}}]
            }})(),

            # Places API response
            type('obj', (object,), {'json': lambda s: {
                'results': [
                    {'name': 'Restaurante 1', 'vicinity': 'Calle 1', 'rating': 4.5},
                    {'name': 'Restaurante 2', 'vicinity': 'Calle 2', 'rating': 4.0}
                ]
            }})()
        ]

        response = self.client.get(self.url, {'city': 'Medellin'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('restaurants', response.data)
        self.assertEqual(len(response.data['restaurants']), 2)
        self.assertTrue(UserAction.objects.filter(user=self.user, action='search_restaurants').exists())

    @patch('restaurants.views.requests.get')
    def test_search_by_lat_lng(self, mock_get):
        """Testea busqueda de restaurantes usando latitud y longitud"""
        # Places API response
        mock_get.return_value.json = lambda: {
            'results': [
                {'name': 'Restaurante 1', 'vicinity': 'Calle 1', 'rating': 4.5}
            ]
        }

        response = self.client.get(self.url, {'lat': 6.2442, 'lng': -75.5812})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('restaurants', response.data)
        self.assertEqual(len(response.data['restaurants']), 1)
        self.assertTrue(UserAction.objects.filter(user=self.user, action='search_restaurants').exists())

    def test_missing_params(self):
        """Testea error cuando faltan parámetros."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_lat_lng(self):
        """Testea error cuando se envían coordenadas inválidas."""
        # Latitud fuera de rango
        response = self.client.get(self.url, {'lat': 100.0, 'lng': -75.5812})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

        # Longitud fuera de rango
        response = self.client.get(self.url, {'lat': 6.2442, 'lng': -200.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
