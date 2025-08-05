from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from common.models import BaseModel
import uuid


class User(AbstractUser):
    """
    Custom User model with additional fields for Map Memories application
    """
    # Override the default username field to allow longer usernames
    username = models.CharField(
        max_length=50,
        unique=True,
        help_text='Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    # UUID field for external references
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    
    # Email field (required)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='Required. Enter a valid email address.'
    )
    
    # Additional profile fields
    full_name = models.CharField(max_length=255, blank=True)
    avatar_url = models.URLField(blank=True, help_text='URL to user avatar image')
    
    # Admin status
    is_admin = models.BooleanField(
        default=False,
        help_text='Designates whether the user can access admin features.'
    )
    
    # Currency system
    currency = models.BigIntegerField(
        default=0,
        help_text='User virtual currency (Xu)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Required fields for registration
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'mm_users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_admin']),
            models.Index(fields=['deleted_at']),
            models.Index(fields=['created_at']),
        ]
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the user"""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using, update_fields=['deleted_at', 'is_active'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the user"""
        return super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted user"""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active'])
    
    @property
    def is_deleted(self):
        """Check if user is soft-deleted"""
        return self.deleted_at is not None
    
    def add_currency(self, amount, description=""):
        """Add currency to user account"""
        self.currency += amount
        self.save(update_fields=['currency'])
        
        # Create transaction log
        from shop.models import TransactionLog
        TransactionLog.objects.create(
            user=self,
            type='admin_add',
            amount=amount,
            description=description or f"Added {amount} currency"
        )
    
    def subtract_currency(self, amount, description=""):
        """Subtract currency from user account"""
        if self.currency >= amount:
            self.currency -= amount
            self.save(update_fields=['currency'])
            
            # Create transaction log
            from shop.models import TransactionLog
            TransactionLog.objects.create(
                user=self,
                type='admin_subtract',
                amount=-amount,
                description=description or f"Subtracted {amount} currency"
            )
            return True
        return False
    
    def can_afford(self, amount):
        """Check if user can afford a purchase"""
        return self.currency >= amount
    
    def get_full_name(self):
        """Return full name or username if full name is not set"""
        return self.full_name or self.username
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class UserSession(models.Model):
    """
    Model to track user sessions for JWT token management
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    token_hash = models.CharField(max_length=255)  # Hash of the JWT token
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mm_user_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_expired(self):
        """Check if session is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Session for {self.user.username}"