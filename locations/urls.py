from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.LocationListView.as_view(), name='location-list'),
    path('<int:pk>/', views.LocationDetailView.as_view(), name='location-detail'),
    path('nearby/', views.NearbyLocationsView.as_view(), name='nearby-locations'),
] 