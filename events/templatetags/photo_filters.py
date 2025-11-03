"""
Custom template filters for Events app
"""
from django import template

register = template.Library()


@register.filter(name='photo_url')
def photo_url(photo):
    """
    Get the correct photo URL - handles both ImageField and direct Cloudinary URLs
    Usage: {{ photo|photo_url }}
    """
    if not photo or not photo.image:
        return ''
    
    return photo.get_image_url()
