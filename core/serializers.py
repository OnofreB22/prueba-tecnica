from rest_framework import serializers
from .models import User, UserAction


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer usuarios"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user
    

class UserActionSerializer(serializers.ModelSerializer):
    """Serializer historial de acciones de cada usuario"""
    class Meta:
        model = UserAction
        fields = ['action', 'timestamp']
