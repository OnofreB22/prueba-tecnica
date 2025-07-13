from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('restaurants/', include('restaurants.urls')),
]

if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
        path(
            'api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
            name='api-docs',
        ),
    ]
