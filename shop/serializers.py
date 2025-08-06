from rest_framework import serializers
from .models import ShopItem, UserItem, TransactionLog


class ShopItemSerializer(serializers.ModelSerializer):
    """
    Serializer for ShopItem model
    """
    class Meta:
        model = ShopItem
        fields = [
            'id', 'name', 'description', 'price', 'item_type',
            'is_active', 'stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserItemSerializer(serializers.ModelSerializer):
    """
    Serializer for UserItem model
    """
    shop_item = ShopItemSerializer(read_only=True)
    
    class Meta:
        model = UserItem
        fields = ['id', 'user', 'shop_item', 'quantity', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TransactionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for TransactionLog model
    """
    class Meta:
        model = TransactionLog
        fields = [
            'id', 'user', 'admin', 'type', 'amount', 'description',
            'shop_item', 'quantity', 'balance_before', 'balance_after',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'admin', 'balance_before', 'balance_after', 'created_at'] 