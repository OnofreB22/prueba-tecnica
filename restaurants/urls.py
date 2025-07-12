from django.urls import path
from .views import NearbyRestaurantsView

urlpatterns = [
    path('nearby/', NearbyRestaurantsView.as_view(), name='nearby_restaurants'),
]
