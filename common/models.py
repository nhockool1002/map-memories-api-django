import uuid
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Manager that includes all objects including soft-deleted ones"""
    
    def get_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Base model with common fields for all models
    Includes UUID, timestamps, and soft delete functionality
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Managers
    objects = SoftDeleteManager()  # Default manager excludes deleted
    all_objects = AllObjectsManager()  # Includes deleted objects
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the object"""
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object"""
        return super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft-deleted object"""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])
    
    @property
    def is_deleted(self):
        """Check if object is soft-deleted"""
        return self.deleted_at is not None
    
    def __str__(self):
        return f"{self.__class__.__name__} ({self.uuid})"


class TimestampedModel(models.Model):
    """
    Model that only includes timestamp fields (for models that don't need soft delete)
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']