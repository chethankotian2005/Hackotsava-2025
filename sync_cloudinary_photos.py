"""
Sync Existing Cloudinary Photos to Database
This script creates database entries for photos already in Cloudinary
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackotsava_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Photo
from events.face_utils import process_photo_faces
from django.core.files.base import ContentFile
import cloudinary
import cloudinary.api
import requests

User = get_user_model()


def sync_cloudinary_photos(event_slug='hackotsava-2025', cloudinary_folder='event_photos/2025/11/03'):
    """
    Sync photos from Cloudinary to database
    
    Args:
        event_slug: Slug of the event
        cloudinary_folder: Folder path in Cloudinary
    """
    
    # Get or create the event
    try:
        event = Event.objects.get(slug=event_slug)
        print(f"✅ Found event: {event.name}")
    except Event.DoesNotExist:
        print(f"❌ Event '{event_slug}' not found!")
        print("\nAvailable events:")
        for e in Event.objects.all():
            print(f"  - {e.slug} ({e.name})")
        return
    
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("⚠️  Admin user not found, using first superuser")
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No superuser found!")
            return
    
    print(f"\n{'='*60}")
    print(f"📸 Syncing Cloudinary Photos")
    print(f"Event: {event.name}")
    print(f"Cloudinary Folder: {cloudinary_folder}")
    print(f"{'='*60}\n")
    
    try:
        # Get photos from Cloudinary folder
        print(f"Fetching photos from Cloudinary...")
        if cloudinary_folder and cloudinary_folder.strip():
            result = cloudinary.api.resources(
                type='upload',
                prefix=cloudinary_folder,
                max_results=500
            )
        else:
            # Get all photos (root folder)
            result = cloudinary.api.resources(
                type='upload',
                max_results=500
            )
        
        cloudinary_photos = result.get('resources', [])
        print(f"Found {len(cloudinary_photos)} photos in Cloudinary\n")
        
        if not cloudinary_photos:
            print("❌ No photos found in Cloudinary folder!")
            print(f"Please check the folder path: {cloudinary_folder}")
            return
        
        synced_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, photo_data in enumerate(cloudinary_photos, 1):
            public_id = photo_data['public_id']
            filename = public_id.split('/')[-1]
            url = photo_data['secure_url']
            
            print(f"[{index}/{len(cloudinary_photos)}] {filename}")
            print(f"  URL: {url}")
            
            try:
                # Check if photo already exists in database
                existing_photo = Photo.objects.filter(image__icontains=filename).first()
                
                if existing_photo:
                    print(f"  ⏭️  Already in database (ID: {existing_photo.id})")
                    skipped_count += 1
                    
                    # Process faces if not done
                    if not existing_photo.faces_processed:
                        try:
                            faces_count = process_photo_faces(existing_photo)
                            print(f"  👤 Detected {faces_count} face(s)")
                        except Exception as e:
                            print(f"  ⚠️  Face processing: {str(e)}")
                    continue
                
                # Create new Photo entry with Cloudinary URL
                photo = Photo(
                    event=event,
                    uploaded_by=admin_user
                )
                
                # Set the image field to the Cloudinary public_id
                photo.image = public_id
                photo.save()
                
                print(f"  ✅ Created database entry")
                synced_count += 1
                
                # Process faces
                try:
                    faces_count = process_photo_faces(photo)
                    print(f"  👤 Detected {faces_count} face(s)")
                except Exception as face_error:
                    print(f"  ⚠️  Face processing: {str(face_error)}")
                
            except Exception as e:
                error_count += 1
                print(f"  ❌ Error: {str(e)}")
        
        print(f"\n{'='*60}")
        print(f"✅ Sync Complete!")
        print(f"Total in Cloudinary: {len(cloudinary_photos)}")
        print(f"Synced to Database: {synced_count}")
        print(f"Skipped (already exists): {skipped_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*60}\n")
        
        if synced_count > 0 or skipped_count > 0:
            print(f"🎉 Photos are now visible at:")
            print(f"   https://hackotsava-images.onrender.com/events/{event_slug}/")
    
    except Exception as e:
        print(f"\n❌ Error accessing Cloudinary: {str(e)}")
        print("\nMake sure your Cloudinary credentials are set in .env file:")
        print("  CLOUDINARY_CLOUD_NAME=...")
        print("  CLOUDINARY_API_KEY=...")
        print("  CLOUDINARY_API_SECRET=...")


if __name__ == "__main__":
    print("\n🔄 Cloudinary Photo Sync Tool\n")
    
    # Default values
    event_slug = 'hackotsava-2025'
    cloudinary_folder = ''  # Empty = root folder
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        folder_arg = sys.argv[1]
        if folder_arg and folder_arg.strip():
            cloudinary_folder = folder_arg
    
    if len(sys.argv) > 2:
        event_slug = sys.argv[2]
    
    print(f"Event: {event_slug}")
    if cloudinary_folder:
        print(f"Cloudinary Folder: {cloudinary_folder}\n")
    else:
        print(f"Cloudinary Folder: ROOT (all photos)\n")
    
    # Run sync
    sync_cloudinary_photos(event_slug, cloudinary_folder)
