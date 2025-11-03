"""
Manually create Photo entries for Cloudinary photos
This bypasses the API and creates entries directly
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackotsava_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Photo
from events.face_utils import process_photo_faces

User = get_user_model()

# Get event and user
event = Event.objects.get(slug='hackotsava-2025')
admin_user = User.objects.filter(is_superuser=True).first()

print(f"\n✅ Event: {event.name}")
print(f"✅ User: {admin_user.username}\n")

# The exact path from your Cloudinary screenshot
# Format: event_photos/2025/11/03/filename.jpg
cloudinary_photos = [
    "event_photos/2025/11/03/photo1.jpg",  # Replace with actual filenames
    "event_photos/2025/11/03/photo2.jpg",  # Replace with actual filenames
    "event_photos/2025/11/03/photo3.jpg",  # Replace with actual filenames
]

print("Creating database entries for Cloudinary photos...\n")

for public_id in cloudinary_photos:
    try:
        # Create Photo entry
        photo = Photo(
            event=event,
            uploaded_by=admin_user,
            image=public_id  # Cloudinary public_id
        )
        photo.save()
        
        print(f"✅ Created: {public_id}")
        print(f"   ID: {photo.id}")
        print(f"   URL: {photo.image.url}")
        
        # Process faces
        try:
            faces_count = process_photo_faces(photo)
            print(f"   👤 Detected {faces_count} face(s)\n")
        except Exception as e:
            print(f"   ⚠️  Face processing: {str(e)}\n")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")

print("="*60)
print("✅ Done! Check your photos at:")
print("   https://hackotsava-images.onrender.com/events/hackotsava-2025/")
print("="*60)
