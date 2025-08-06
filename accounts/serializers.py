from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from shop.serializers import UserItemSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes additional user information
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['full_name'] = self.user.full_name
        data['is_admin'] = self.user.is_admin
        data['currency'] = self.user.currency
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'full_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile with owned items
    """
    owned_items = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'currency', 'owned_items', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_owned_items(self, obj):
        """Get all items owned by the user"""
        from shop.models import UserItem
        user_items = UserItem.objects.filter(user=obj)
        return UserItemSerializer(user_items, many=True).data 