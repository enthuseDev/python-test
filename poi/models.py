from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PointOfInterest(models.Model):
    # Internal ID (auto-generated primary key)
    internal_id = models.AutoField(primary_key=True)
    
    # External ID from the source file
    external_id = models.CharField(max_length=100, db_index=True)
    
    # PoI name
    name = models.CharField(max_length=255)
    
    # Coordinates
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    # Category
    category = models.CharField(max_length=100, db_index=True)
    
    # Ratings (stored as JSON array of individual ratings)
    ratings_data = models.JSONField(default=list, blank=True)
    
    # Average rating (calculated field)
    avg_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Optional description (from JSON files)
    description = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Point of Interest"
        verbose_name_plural = "Points of Interest"
        ordering = ['name']
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['category']),
            models.Index(fields=['avg_rating']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.external_id})"
    
    def save(self, *args, **kwargs):
        # Calculate average rating before saving
        if self.ratings_data:
            try:
                ratings = [float(r) for r in self.ratings_data if r is not None]
                if ratings:
                    self.avg_rating = sum(ratings) / len(ratings)
                else:
                    self.avg_rating = None
            except (ValueError, TypeError):
                self.avg_rating = None
        else:
            self.avg_rating = None
        
        super().save(*args, **kwargs)
    
    @property
    def rating_count(self):
        """Return the number of ratings"""
        if self.ratings_data:
            return len([r for r in self.ratings_data if r is not None])
        return 0
