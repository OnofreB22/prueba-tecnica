from django.test import TestCase
from core.models import User, UserAction


class UserModelTest(TestCase):
    """Pruebas unitarias para el modelo User"""
    def test_create_user_with_email(self):
        """Test creacion exitosa de usuario"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(str(user), 'test@example.com')

    def test_email_is_unique(self):
        """Test usuario con email unico"""
        User.objects.create_user(email='unique@example.com', username='user1', password='pass')
        with self.assertRaises(Exception):
            User.objects.create_user(email='unique@example.com', username='user2', password='pass')


class UserActionModelTest(TestCase):
    """Pruebas unitarias para el modelo UserAction"""
    def setUp(self):
        self.user = User.objects.create_user(
            email='action@example.com',
            username='actionuser',
            password='testpass'
        )

    def test_create_user_action(self):
        """Test registrar accion de crear usuario"""
        action = UserAction.objects.create(
            user=self.user,
            action='signup'
        )
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.action, 'signup')
        self.assertIsNotNone(action.timestamp)

    def test_action_choices(self):
        """Test resgistrar solo accion de la lista de opciones"""
        valid_action = UserAction.objects.create(user=self.user, action='login')
        self.assertEqual(valid_action.action, 'login')
        # Test invalid action
        with self.assertRaises(ValueError):
            UserAction.objects.create(user=self.user, action='invalid_action')
