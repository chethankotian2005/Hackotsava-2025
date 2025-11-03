"""
Manual Photo Upload Script
Upload photos directly to Cloudinary and create database entries

INSTRUCTIONS:
1. Place your photos in a folder (e.g., "photos_to_upload")
2. Run: python manual_upload_photos.py
3. Photos will be uploaded to Cloudinary and added to the database
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

from django.core.files import File
from django.contrib.auth import get_user_model
from events.models import Event, Photo
from events.face_utils import process_photo_faces
import cloudinary
import cloudinary.uploader

User = get_user_model()

def upload_photos_to_event(photos_folder, event_slug='hackotsava-2025'):
    """
    Upload all photos from a folder to an event
    
    Args:
        photos_folder: Path to folder containing photos
        event_slug: Slug of the event (default: hackotsava-2025)
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
    
    # Get or create admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("⚠️  Admin user not found, using first superuser")
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No superuser found! Please create one first.")
            return
    
    # Check if folder exists
    if not os.path.exists(photos_folder):
        print(f"❌ Folder '{photos_folder}' not found!")
        print(f"Current directory: {os.getcwd()}")
        return
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    photo_files = [
        f for f in os.listdir(photos_folder)
        if os.path.splitext(f.lower())[1] in image_extensions
    ]
    
    if not photo_files:
        print(f"❌ No image files found in '{photos_folder}'")
        return
    
    print(f"\n{'='*60}")
    print(f"📸 Starting upload of {len(photo_files)} photos")
    print(f"Event: {event.name}")
    print(f"Folder: {photos_folder}")
    print(f"{'='*60}\n")
    
    uploaded_count = 0
    error_count = 0
    
    for index, filename in enumerate(photo_files, 1):
        file_path = os.path.join(photos_folder, filename)
        print(f"[{index}/{len(photo_files)}] {filename}")
        
        try:
            # Open and upload the photo
            with open(file_path, 'rb') as photo_file:
                # Create Photo object - Django + Cloudinary will handle upload
                django_file = File(photo_file, name=filename)
                photo = Photo.objects.create(
                    event=event,
                    image=django_file,
                    uploaded_by=admin_user
                )
            
            print(f"  ✅ Uploaded to Cloudinary")
            print(f"  📍 URL: {photo.image.url}")
            uploaded_count += 1
            
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
    print(f"✅ Upload Complete!")
    print(f"Total: {len(photo_files)}")
    print(f"Uploaded: {uploaded_count}")
    print(f"Failed: {error_count}")
    print(f"{'='*60}\n")
    
    if uploaded_count > 0:
        print(f"🎉 Photos are now visible at:")
        print(f"   https://hackotsava-images.onrender.com/events/{event_slug}/")


def list_cloudinary_info():
    """Show Cloudinary configuration"""
    from django.conf import settings
    
    print("\n" + "="*60)
    print("📦 CLOUDINARY CONFIGURATION")
    print("="*60)
    print(f"Cloud Name: {settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'Not set')}")
    print(f"Storage: {settings.DEFAULT_FILE_STORAGE}")
    print("\n📁 Upload Paths:")
    print(f"   Event Photos: event_photos/%Y/%m/%d/")
    print(f"   Example: event_photos/2025/11/03/photo.jpg")
    print("\n🌐 Direct Cloudinary Upload:")
    print(f"   Login to: https://cloudinary.com/console")
    print(f"   Go to: Media Library → Upload")
    print(f"   Folder: event_photos/2025/11/03/")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n🎨 Manual Photo Upload Tool\n")
    
    # Show Cloudinary info
    list_cloudinary_info()
    
    # Check for command line argument
    if len(sys.argv) > 1:
        photos_folder = sys.argv[1]
    else:
        photos_folder = input("Enter path to photos folder (e.g., 'photos_to_upload'): ").strip()
    
    if not photos_folder:
        print("\n❌ No folder specified!")
        print("\nUsage:")
        print("  python manual_upload_photos.py <folder_path>")
        print("\nExample:")
        print("  python manual_upload_photos.py photos_to_upload")
        sys.exit(1)
    
    # Ask for event slug
    event_slug = input("Enter event slug (default: hackotsava-2025): ").strip()
    if not event_slug:
        event_slug = 'hackotsava-2025'
    
    # Upload photos
    upload_photos_to_event(photos_folder, event_slug)
