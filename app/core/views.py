from rest_framework import generics, permissions
from .serializers import UserRegisterSerializer, UserActionSerializer
from .models import User, UserAction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """Vista para crear usuarios"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        # Registrar accion de signup
        UserAction.objects.create(user=user, action='signup')


class LogoutView(APIView):
    """Vista para hacer logout"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # Invalidar refresh token agregandolo a la blacklist
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Registrar accion de logout
            UserAction.objects.create(user=request.user, action='logout')

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserActionListView(generics.ListAPIView):
    """Vista para obtener historial de transacciones del usuario"""
    serializer_class = UserActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAction.objects.filter(user=self.request.user).order_by('-timestamp')


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista para login y obtencion de token"""
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Si el login fue exitoso, registrar la accion
        if response.status_code == 200:
            user = User.objects.filter(email=request.data.get('email')).first()
            if user:
                UserAction.objects.create(user=user, action='login')
        return response
