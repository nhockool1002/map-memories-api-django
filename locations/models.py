from django.contrib.gis.db import models as gis_models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseModel
from accounts.models import User


class Location(BaseModel):
    """
    Location model with geospatial capabilities using PostGIS
    """
    name = models.CharField(
        max_length=255,
        help_text='Name of the location'
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed description of the location'
    )
    
    # Geospatial fields
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        help_text='Latitude coordinate (-90 to 90)'
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text='Longitude coordinate (-180 to 180)'
    )
    
    # PostGIS Point field for efficient geospatial queries
    point = gis_models.PointField(
        srid=4326,  # WGS84 coordinate system
        help_text='Point geometry for geospatial queries',
        null=True,
        blank=True
    )
    
    # Address information
    address = models.TextField(
        blank=True,
        help_text='Full address of the location'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='Country name'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text='City name'
    )
    
    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='locations',
        help_text='User who created this location'
    )
    
    marker_item = models.ForeignKey(
        'shop.ShopItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations_using_marker',
        help_text='Custom marker item for this location (optional)'
    )
    
    class Meta:
        db_table = 'mm_locations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
            models.Index(fields=['marker_item']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to create Point geometry from lat/lng"""
        if self.latitude is not None and self.longitude is not None:
            from django.contrib.gis.geos import Point
            self.point = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)
    
    def delete(self, using=None, keep_parents=False):
        """Override delete to also soft delete related memories"""
        # Soft delete related memories
        from memories.models import Memory
        Memory.objects.filter(location=self).delete()
        
        # Soft delete this location
        super().delete(using=using, keep_parents=keep_parents)
    
    @property
    def memory_count(self):
        """Get count of memories at this location"""
        return self.memories.count()
    
    @property
    def public_memory_count(self):
        """Get count of public memories at this location"""
        return self.memories.filter(is_public=True).count()
    
    def get_nearby_locations(self, radius_km=5, limit=20):
        """
        Get nearby locations within specified radius
        
        Args:
            radius_km: Radius in kilometers (default: 5)
            limit: Maximum number of results (default: 20)
        
        Returns:
            QuerySet of nearby Location objects
        """
        if not self.point:
            return Location.objects.none()
        
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        
        return (Location.objects
                .filter(point__distance_lte=(self.point, D(km=radius_km)))
                .exclude(id=self.id)
                .annotate(distance=Distance('point', self.point))
                .order_by('distance')[:limit])
    
    @classmethod
    def find_nearby(cls, latitude, longitude, radius_km=5, limit=20):
        """
        Find locations near given coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers (default: 5)
            limit: Maximum number of results (default: 20)
        
        Returns:
            QuerySet of nearby Location objects with distance annotation
        """
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance
        
        point = Point(float(longitude), float(latitude), srid=4326)
        
        return (cls.objects
                .filter(point__distance_lte=(point, D(km=radius_km)))
                .annotate(distance=Distance('point', point))
                .order_by('distance')[:limit])
    
    def distance_to(self, other_location):
        """
        Calculate distance to another location
        
        Args:
            other_location: Another Location instance
        
        Returns:
            Distance in kilometers (float)
        """
        if not self.point or not other_location.point:
            return None
        
        return self.point.distance(other_location.point) * 111.32  # Convert degrees to km
    
    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"