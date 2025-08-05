from rest_framework import serializers
from .models import Memory, MemoryLike
from locations.serializers import LocationSerializer


class MemorySerializer(serializers.ModelSerializer):
    """
    Serializer for Memory model
    """
    location = LocationSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Memory
        fields = [
            'id', 'user', 'location', 'title', 'content', 'visit_date',
            'is_public', 'tags', 'like_count', 'is_liked_by_user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MemoryLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for MemoryLike model
    """
    class Meta:
        model = MemoryLike
        fields = ['id', 'user', 'memory', 'created_at']
        read_only_fields = ['id', 'created_at'] 