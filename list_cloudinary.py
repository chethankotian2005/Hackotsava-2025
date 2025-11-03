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
    
    # List ALL photos (no prefix filter)
    print("\n📸 ALL Photos in Cloudinary (first 20):\n")
    try:
        photos = cloudinary.api.resources(
            type='upload',
            max_results=20
        )
        
        if photos.get('resources'):
            for photo in photos['resources']:
                print(f"  - {photo['public_id']}")
                print(f"    URL: {photo['secure_url'][:80]}...")
        else:
            print("  No photos found")
    except Exception as e:
        print(f"  Error: {e}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nMake sure Cloudinary credentials are set in .env")
