from django.contrib import admin
from .models import PointOfInterest


@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = [
        'internal_id',
        'name', 
        'external_id',
        'category',
        'avg_rating',
        'rating_count',
        'latitude',
        'longitude'
    ]
    
    list_filter = [
        'category',
        'avg_rating',
        'created_at'
    ]
    
    search_fields = [
        'internal_id',
        'external_id',
        'name',
        'category'
    ]
    
    readonly_fields = [
        'internal_id',
        'avg_rating',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('internal_id', 'external_id', 'name', 'category')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Ratings', {
            'fields': ('ratings_data', 'avg_rating')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['name']
    
    def rating_count(self, obj):
        """Display the number of ratings"""
        return obj.rating_count
    rating_count.short_description = 'Rating Count'
