"""
List all folders and photos in Cloudinary
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackotsava_project.settings')
django.setup()

import cloudinary
import cloudinary.api

try:
    # List root folders
    print("\n📁 Cloudinary Folders:\n")
    result = cloudinary.api.root_folders()
    for folder in result.get('folders', []):
        print(f"  - {folder['name']}/")
    
    # Try to list photos in event_photos
    print("\n📸 Photos in event_photos:\n")
    try:
        photos = cloudinary.api.resources(
            type='upload',
            prefix='event_photos',
            max_results=100
        )
        
        for photo in photos.get('resources', []):
            print(f"  - {photo['public_id']}")
            print(f"    URL: {photo['secure_url']}")
    except Exception as e:
        print(f"  No photos found or error: {e}")
    
    # Try media/event_photos
    print("\n📸 Photos in media/event_photos:\n")
    try:
        photos = cloudinary.api.resources(
            type='upload',
            prefix='media/event_photos',
            max_results=100
        )
        
        for photo in photos.get('resources', []):
            print(f"  - {photo['public_id']}")
            print(f"    URL: {photo['secure_url']}")
    except Exception as e:
        print(f"  No photos found or error: {e}")
    
    # Try just media/
    print("\n📸 Photos in media/:\n")
    try:
        photos = cloudinary.api.resources(
            type='upload',
            prefix='media/',
            max_results=100
        )
        
        for photo in photos.get('resources', []):
            print(f"  - {photo['public_id']}")
            print(f"    URL: {photo['secure_url']}")
    except Exception as e:
        print(f"  No photos found or error: {e}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nMake sure Cloudinary credentials are set in .env")
