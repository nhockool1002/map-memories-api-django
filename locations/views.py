from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Location
from .serializers import LocationSerializer


class LocationListView(generics.ListCreateAPIView):
    """
    List and create locations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)


class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and delete location
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)


class NearbyLocationsView(generics.ListAPIView):
    """
    Get nearby locations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        # This is a placeholder - implement actual nearby logic
        return Location.objects.all() 