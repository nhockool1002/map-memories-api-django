from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import ShopItem, UserItem, TransactionLog
from .serializers import ShopItemSerializer, UserItemSerializer, TransactionLogSerializer

User = get_user_model()


class ShopItemListView(generics.ListAPIView):
    """
    List all shop items
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShopItemSerializer
    queryset = ShopItem.objects.filter(is_active=True)


class ShopItemDetailView(generics.RetrieveAPIView):
    """
    Get shop item details
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ShopItemSerializer
    queryset = ShopItem.objects.filter(is_active=True)


class PurchaseItemView(generics.CreateAPIView):
    """
    Purchase an item
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionLogSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserInventoryView(generics.ListAPIView):
    """
    Get user's inventory
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserItemSerializer
    
    def get_queryset(self):
        return UserItem.objects.filter(user=self.request.user)


# Currency views
class CurrencyBalanceView(generics.RetrieveAPIView):
    """
    Get user's currency balance
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return Response({
            'currency': user.currency,
            'username': user.username
        })


class TransactionHistoryView(generics.ListAPIView):
    """
    Get user's transaction history
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionLogSerializer
    
    def get_queryset(self):
        return TransactionLog.objects.filter(user=self.request.user).order_by('-created_at')


# Admin views
class AdminUserListView(generics.ListAPIView):
    """
    Admin: List all users
    """
    permission_classes = [IsAdminUser]
    serializer_class = UserItemSerializer  # Placeholder serializer
    
    def get_queryset(self):
        return User.objects.all()


class AdminTransactionListView(generics.ListAPIView):
    """
    Admin: List all transactions
    """
    permission_classes = [IsAdminUser]
    serializer_class = TransactionLogSerializer
    
    def get_queryset(self):
        return TransactionLog.objects.all().order_by('-created_at')


class AdminAddCurrencyView(generics.GenericAPIView):
    """
    Admin: Add currency to user
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        
        try:
            user = User.objects.get(id=user_id)
            user.currency += amount
            user.save()
            
            TransactionLog.objects.create(
                user=user,
                admin=request.user,
                type='admin_add',
                amount=amount,
                description=f'Currency added by admin',
                balance_before=user.currency - amount,
                balance_after=user.currency
            )
            
            return Response({
                'success': True,
                'new_balance': user.currency
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            ) 