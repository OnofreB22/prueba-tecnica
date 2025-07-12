from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import UserRegisterView, LogoutView, UserActionListView, CustomTokenObtainPairView
from django.urls import path

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', UserRegisterView.as_view(), name='user_register'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/actions/', UserActionListView.as_view(), name='user_actions'),
]
