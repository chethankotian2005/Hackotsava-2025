"""
Models for Events App - Event, Photo, FaceEncoding
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Event(models.Model):
    """
    Event model to store event information
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the event"
    )
    
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the event name"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Event description"
    )
    
    event_date = models.DateField(
        help_text="Date when the event took place"
    )
    
    location = models.CharField(
        max_length=300,
        blank=True,
        help_text="Event location"
    )
    
    cover_image = models.ImageField(
        upload_to='event_covers/',
        blank=True,
        null=True,
        help_text="Cover image for the event"
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Whether the event is publicly visible"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date', '-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['-event_date']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_photo_count(self):
        """Get total number of photos in this event"""
        return self.photos.count()
    
    def get_face_count(self):
        """Get total number of detected faces in this event"""
        return FaceEncoding.objects.filter(photo__event=self).count()


class Photo(models.Model):
    """
    Photo model to store event photos
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos',
        help_text="Event this photo belongs to"
    )
    
    image = models.ImageField(
        upload_to='event_photos/%Y/%m/%d/',
        help_text="Event photo file"
    )
    
    thumbnail = models.ImageField(
        upload_to='event_photos/thumbnails/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Thumbnail version of the photo"
    )
    
    caption = models.CharField(
        max_length=500,
        blank=True,
        help_text="Photo caption"
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_photos'
    )
    
    faces_processed = models.BooleanField(
        default=False,
        help_text="Whether face detection has been completed for this photo"
    )
    
    face_count = models.IntegerField(
        default=0,
        help_text="Number of faces detected in this photo"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        indexes = [
            models.Index(fields=['event', '-uploaded_at']),
            models.Index(fields=['faces_processed']),
        ]
    
    def __str__(self):
        return f"Photo in {self.event.name} - {self.uploaded_at.strftime('%Y-%m-%d')}"


class FaceEncoding(models.Model):
    """
    Store face encodings extracted from photos for face recognition
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        related_name='face_encodings',
        help_text="Photo this face encoding belongs to"
    )
    
    # Store face encoding as comma-separated string (128 dimensions)
    encoding = models.TextField(
        help_text="Face encoding data (128-dimension vector stored as text)"
    )
    
    # Bounding box coordinates for the face in the photo
    top = models.IntegerField(help_text="Top coordinate of face bounding box")
    right = models.IntegerField(help_text="Right coordinate of face bounding box")
    bottom = models.IntegerField(help_text="Bottom coordinate of face bounding box")
    left = models.IntegerField(help_text="Left coordinate of face bounding box")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Face Encoding'
        verbose_name_plural = 'Face Encodings'
        indexes = [
            models.Index(fields=['photo']),
        ]
    
    def __str__(self):
        return f"Face in {self.photo}"
    
    def get_encoding_array(self):
        """Convert stored encoding string back to numpy array"""
        import numpy as np
        return np.array([float(x) for x in self.encoding.split(',')])
    
    def get_face_location(self):
        """Return face location as tuple (top, right, bottom, left)"""
        return (self.top, self.right, self.bottom, self.left)


class SearchHistory(models.Model):
    """
    Track user search history for analytics
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='searches'
    )
    
    matches_found = models.IntegerField(
        default=0,
        help_text="Number of photos matched"
    )
    
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
    
    def __str__(self):
        return f"{self.user.username} searched {self.event.name} - Found {self.matches_found} matches"
