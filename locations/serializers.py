from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for Location model
    """
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'description', 'latitude', 'longitude', 
            'address', 'city', 'country', 'marker_item', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 