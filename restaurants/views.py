import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from core.models import UserAction

class NearbyRestaurantsView(APIView):
    """Vista para obtener los restaurantes cercanos a la ubicacion"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get('city')
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        api_key = settings.GOOGLE_MAPS_API_KEY

        # Verificar que lat/long sean validos
        try:
            if lat is not None and lng is not None:
                lat = float(lat)
                lng = float(lng)
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    return Response({'error': 'Coordenadas inválidas'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'Coordenadas inválidas'}, status=400)
    

        # Si se proporciona ciudad, consular Geocoding API para obtener coordenadas
        if city:
            geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={api_key}"
            geo_resp = requests.get(geo_url).json()
            if geo_resp['status'] != 'OK':
                return Response({'error': 'Ciudad no encontrada'}, status=400)
            location = geo_resp['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']

        # Si no hay lat/lng, retornar error
        if not lat or not lng:
            return Response({'error': 'Debes enviar los parámetros city o lat y lng.'}, status=400)

        # Registrar acción de busqueda de restaurantes
        UserAction.objects.create(user=request.user, action='search_restaurants')

        # Buscar restaurantes cercanos
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius=2000&type=restaurant&key={api_key}"
        )
        places_resp = requests.get(places_url).json()
        results = [
            {
                'name': r['name'],
                'address': r.get('vicinity'),
                'rating': r.get('rating'),
            }
            for r in places_resp.get('results', [])
        ]
        return Response({'restaurants': results})
