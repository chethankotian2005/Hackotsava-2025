from django.contrib import admin
from .models import Event, Photo, FaceEncoding, SearchHistory


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for Event model
    """
    list_display = ['name', 'event_date', 'location', 'is_public', 'created_by', 'get_photo_count', 'created_at']
    list_filter = ['is_public', 'event_date', 'created_at']
    search_fields = ['name', 'description', 'location']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'event_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'event_date', 'location')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Settings', {
            'fields': ('is_public', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """
    Admin interface for Photo model
    """
    list_display = ['event', 'uploaded_by', 'faces_processed', 'face_count', 'uploaded_at']
    list_filter = ['faces_processed', 'uploaded_at', 'event']
    search_fields = ['caption', 'event__name']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'


@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    """
    Admin interface for FaceEncoding model
    """
    list_display = ['photo', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__event__name']
    readonly_fields = ['created_at', 'encoding']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for SearchHistory model
    """
    list_display = ['user', 'event', 'matches_found', 'searched_at']
    list_filter = ['searched_at', 'event']
    search_fields = ['user__username', 'event__name']
    readonly_fields = ['searched_at']
    date_hierarchy = 'searched_at'
