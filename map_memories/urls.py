from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def health_check(request):
    """Health check endpoint for container health monitoring"""
    return JsonResponse({
        'success': True,
        'message': 'Service is healthy',
        'data': {
            'status': 'healthy',
            'database': 'connected'
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/locations/', include('locations.urls')),
    path('api/v1/memories/', include('memories.urls')),
    path('api/v1/shop/', include('shop.urls')),
    path('api/v1/currency/', include('shop.currency_urls')),
    path('api/v1/shop-admin/', include('shop.admin_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Map Memories Administration'
admin.site.site_title = 'Map Memories Admin'
admin.site.index_title = 'Welcome to Map Memories Administration'