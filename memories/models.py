from django.db import models
from django.contrib.postgres.fields import ArrayField
from common.models import BaseModel
from accounts.models import User


class Memory(BaseModel):
    """
    Memory model representing a user's memory at a specific location
    
    Note: Changed to OneToOneField with Location as per requirement
    When memory is deleted, location should also be deleted
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memories',
        help_text='User who created this memory'
    )
    
    # One-to-one relationship with Location
    # When memory is deleted, location is also deleted
    location = models.OneToOneField(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='memory',
        null=True,
        blank=True,
        help_text='Location associated with this memory (1-1 relationship)'
    )
    
    title = models.CharField(
        max_length=255,
        help_text='Title of the memory'
    )
    
    content = models.TextField(
        help_text='Detailed content/description of the memory'
    )
    
    visit_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the user visited this place'
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text='Whether this memory is visible to other users'
    )
    
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text='Tags associated with this memory'
    )
    
    class Meta:
        db_table = 'mm_memories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['location']),
            models.Index(fields=['is_public']),
            models.Index(fields=['visit_date']),
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
        ]
    
    def delete(self, using=None, keep_parents=False):
        """Override delete to also delete related location (1-1 relationship)"""
        # Delete related location if it exists
        if self.location:
            self.location.delete()
        
        # Soft delete this memory
        super().delete(using=using, keep_parents=keep_parents)
    
    @property
    def like_count(self):
        """Get count of likes for this memory"""
        return self.likes.count()
    
    @property
    def media_count(self):
        """Get count of media attachments for this memory"""
        return self.media_files.count()
    
    def is_liked_by(self, user):
        """Check if memory is liked by specific user"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def toggle_like(self, user):
        """Toggle like status for this memory by user"""
        like, created = MemoryLike.objects.get_or_create(
            user=user,
            memory=self
        )
        if not created:
            like.delete()
            return False  # Unlike
        return True  # Like
    
    def add_tags(self, new_tags):
        """Add new tags to memory"""
        if isinstance(new_tags, str):
            new_tags = [tag.strip() for tag in new_tags.split(',')]
        
        # Clean and normalize tags
        clean_tags = [tag.lower().strip() for tag in new_tags if tag.strip()]
        
        # Add only new tags
        for tag in clean_tags:
            if tag not in self.tags:
                self.tags.append(tag)
        
        self.save(update_fields=['tags'])
    
    def remove_tags(self, tags_to_remove):
        """Remove tags from memory"""
        if isinstance(tags_to_remove, str):
            tags_to_remove = [tag.strip() for tag in tags_to_remove.split(',')]
        
        # Normalize tags to remove
        clean_tags = [tag.lower().strip() for tag in tags_to_remove]
        
        # Remove tags
        self.tags = [tag for tag in self.tags if tag not in clean_tags]
        self.save(update_fields=['tags'])
    
    @classmethod
    def get_public_memories(cls):
        """Get all public memories"""
        return cls.objects.filter(is_public=True)
    
    @classmethod
    def search_by_tags(cls, tags, user=None):
        """Search memories by tags"""
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]
        
        # Normalize tags
        clean_tags = [tag.lower().strip() for tag in tags if tag.strip()]
        
        queryset = cls.objects.filter(tags__overlap=clean_tags)
        
        # If user is not provided or not authenticated, only show public memories
        if not user or not user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        else:
            # Show user's own memories or public memories
            queryset = queryset.filter(
                models.Q(user=user) | models.Q(is_public=True)
            )
        
        return queryset.distinct()
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"


class MemoryLike(models.Model):
    """
    Model to track memory likes by users
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memory_likes'
    )
    memory = models.ForeignKey(
        Memory,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mm_memory_likes'
        unique_together = ['user', 'memory']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['memory']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.memory.title}"