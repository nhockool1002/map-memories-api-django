from django.db import models
from django.core.validators import MinValueValidator
from common.models import BaseModel
from accounts.models import User


class ShopItem(BaseModel):
    """
    Model for items available in the shop (markers, decorations, etc.)
    """
    
    ITEM_TYPE_CHOICES = [
        ('marker', 'Marker'),
        ('decoration', 'Decoration'),
        ('theme', 'Theme'),
        ('effect', 'Effect'),
    ]
    
    name = models.CharField(
        max_length=255,
        help_text='Name of the shop item'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Description of the shop item'
    )
    
    image_base64 = models.TextField(
        help_text='Base64 encoded image data URL for the item'
    )
    
    price = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text='Price in virtual currency (Xu)'
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        help_text='Available stock quantity'
    )
    
    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES,
        default='marker',
        help_text='Type of item'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this item is available for purchase'
    )
    
    # Optional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional metadata for the item'
    )
    
    class Meta:
        db_table = 'mm_shop_items'
        ordering = ['item_type', 'name']
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
        ]
    
    @property
    def is_available(self):
        """Check if item is available for purchase"""
        return self.is_active and self.stock > 0
    
    @property
    def total_sold(self):
        """Get total quantity sold"""
        return sum(self.user_items.values_list('quantity', flat=True))
    
    def reduce_stock(self, quantity):
        """Reduce stock by specified quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save(update_fields=['stock'])
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock by specified quantity"""
        self.stock += quantity
        self.save(update_fields=['stock'])
    
    def __str__(self):
        return f"{self.name} ({self.item_type}) - {self.price} Xu"


class UserItem(BaseModel):
    """
    Model for tracking items owned by users
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_items'
    )
    
    shop_item = models.ForeignKey(
        ShopItem,
        on_delete=models.CASCADE,
        related_name='user_items'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Quantity owned by user'
    )
    
    class Meta:
        db_table = 'mm_user_items'
        unique_together = ['user', 'shop_item']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['shop_item']),
            models.Index(fields=['quantity']),
        ]
    
    def increase_quantity(self, amount=1):
        """Increase quantity owned"""
        self.quantity += amount
        self.save(update_fields=['quantity'])
    
    def decrease_quantity(self, amount=1):
        """Decrease quantity owned"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save(update_fields=['quantity'])
            return True
        elif self.quantity == amount:
            self.delete()
            return True
        return False
    
    def __str__(self):
        return f"{self.user.username} owns {self.quantity}x {self.shop_item.name}"


class TransactionLog(models.Model):
    """
    Model for tracking all currency transactions
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('admin_add', 'Admin Add'),
        ('admin_subtract', 'Admin Subtract'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transaction_logs'
    )
    
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_transactions',
        help_text='Admin user who performed the transaction (if applicable)'
    )
    
    type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text='Type of transaction'
    )
    
    amount = models.BigIntegerField(
        help_text='Transaction amount (positive for add, negative for subtract)'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Description of the transaction'
    )
    
    # Optional reference to related objects
    shop_item = models.ForeignKey(
        ShopItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text='Shop item involved in transaction (if applicable)'
    )
    
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Quantity of items purchased (if applicable)'
    )
    
    # Balance information
    balance_before = models.BigIntegerField(
        help_text='User balance before transaction'
    )
    
    balance_after = models.BigIntegerField(
        help_text='User balance after transaction'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mm_transaction_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['admin']),
            models.Index(fields=['type']),
            models.Index(fields=['shop_item']),
            models.Index(fields=['created_at']),
        ]
    
    @classmethod
    def create_purchase_log(cls, user, shop_item, quantity, amount):
        """Create transaction log for purchase"""
        balance_before = user.currency + amount  # Before deduction
        balance_after = user.currency  # After deduction
        
        return cls.objects.create(
            user=user,
            type='purchase',
            amount=-amount,  # Negative for spending
            description=f"Purchased {quantity}x {shop_item.name}",
            shop_item=shop_item,
            quantity=quantity,
            balance_before=balance_before,
            balance_after=balance_after
        )
    
    @classmethod
    def create_admin_log(cls, user, admin, transaction_type, amount, description=""):
        """Create transaction log for admin actions"""
        balance_before = user.currency
        
        if transaction_type == 'admin_add':
            balance_after = balance_before + amount
        else:  # admin_subtract
            balance_after = balance_before - amount
            amount = -amount  # Make negative for subtract
        
        return cls.objects.create(
            user=user,
            admin=admin,
            type=transaction_type,
            amount=amount,
            description=description,
            balance_before=balance_before,
            balance_after=balance_after
        )
    
    def __str__(self):
        return f"{self.type}: {self.amount} Xu for {self.user.username}"


class PurchaseManager:
    """
    Manager class for handling purchase transactions
    """
    
    @staticmethod
    def purchase_item(user, shop_item, quantity=1):
        """
        Handle item purchase transaction
        
        Returns:
            (success: bool, message: str, user_item: UserItem or None)
        """
        from django.db import transaction
        
        # Validate purchase
        if not shop_item.is_available:
            return False, "Item is not available", None
        
        if shop_item.stock < quantity:
            return False, f"Insufficient stock. Available: {shop_item.stock}", None
        
        total_cost = shop_item.price * quantity
        
        if not user.can_afford(total_cost):
            return False, f"Insufficient balance. Required: {total_cost}, Available: {user.currency}", None
        
        # Perform transaction
        with transaction.atomic():
            # Deduct currency
            user.currency -= total_cost
            user.save(update_fields=['currency'])
            
            # Reduce stock
            shop_item.reduce_stock(quantity)
            
            # Add to user items
            user_item, created = UserItem.objects.get_or_create(
                user=user,
                shop_item=shop_item,
                defaults={'quantity': quantity}
            )
            
            if not created:
                user_item.increase_quantity(quantity)
            
            # Create transaction log
            TransactionLog.create_purchase_log(user, shop_item, quantity, total_cost)
        
        return True, "Purchase successful", user_item
    
    @staticmethod
    def admin_add_currency(user, admin, amount, description=""):
        """
        Admin adds currency to user account
        
        Returns:
            (success: bool, message: str)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        from django.db import transaction
        
        with transaction.atomic():
            user.currency += amount
            user.save(update_fields=['currency'])
            
            TransactionLog.create_admin_log(user, admin, 'admin_add', amount, description)
        
        return True, f"Added {amount} currency to {user.username}"
    
    @staticmethod
    def admin_subtract_currency(user, admin, amount, description=""):
        """
        Admin subtracts currency from user account
        
        Returns:
            (success: bool, message: str)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        if user.currency < amount:
            return False, f"Insufficient balance. User has: {user.currency}, Requested: {amount}"
        
        from django.db import transaction
        
        with transaction.atomic():
            user.currency -= amount
            user.save(update_fields=['currency'])
            
            TransactionLog.create_admin_log(user, admin, 'admin_subtract', amount, description)
        
        return True, f"Subtracted {amount} currency from {user.username}"