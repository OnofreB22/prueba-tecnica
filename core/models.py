from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Usuario basico"""
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserAction(models.Model):
    """Registro de transacciones del usuario"""
    ACTION_CHOICES = [
        ('signup', 'Signup'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('search_restaurants', 'Search Restaurants'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validación personalizada"""
        super().clean()
        valid_actions = [choice[0] for choice in self.ACTION_CHOICES]
        if self.action not in valid_actions:
            raise ValueError(f"'{self.action}' no es una acción válida. Opciones permitidas: {valid_actions}")
    
    def save(self, *args, **kwargs):
        """Override del método save para ejecutar validación"""
        self.clean()
        super().save(*args, **kwargs)