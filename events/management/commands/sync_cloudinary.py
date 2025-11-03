"""
Django management command to sync Cloudinary photos to database
Usage: python manage.py sync_cloudinary
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event, Photo
import cloudinary
import cloudinary.api
from decouple import config
import requests
from io import BytesIO
from PIL import Image

class Command(BaseCommand):
    help = 'Sync photos from Cloudinary to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event-slug',
            type=str,
            default='hackotsava-2025',
            help='Event slug to associate photos with (default: hackotsava-2025)'
        )
        parser.add_argument(
            '--folder',
            type=str,
            default='',
            help='Cloudinary folder path (empty for root folder)'
        )
        parser.add_argument(
            '--no-face-detection',
            action='store_true',
            help='Skip face detection (faster)'
        )

    def handle(self, *args, **options):
        event_slug = options['event_slug']
        cloudinary_folder = options['folder']
        skip_face_detection = options['no_face_detection']
        
        self.stdout.write(f"🔄 Starting Cloudinary sync...")
        self.stdout.write(f"   Event: {event_slug}")
        self.stdout.write(f"   Folder: {'ROOT (all photos)' if not cloudinary_folder else cloudinary_folder}")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=config('CLOUDINARY_CLOUD_NAME'),
            api_key=config('CLOUDINARY_API_KEY'),
            api_secret=config('CLOUDINARY_API_SECRET')
        )
        
        # Get event
        try:
            event = Event.objects.get(slug=event_slug)
            self.stdout.write(self.style.SUCCESS(f"✓ Found event: {event.name}"))
        except Event.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"✗ Event with slug '{event_slug}' not found"))
            return
        
        # Fetch photos from Cloudinary
        self.stdout.write(f"\n📡 Fetching photos from Cloudinary...")
        
        try:
            if cloudinary_folder.strip():
                resources = cloudinary.api.resources(
                    type='upload',
                    prefix=cloudinary_folder,
                    max_results=500
                )
            else:
                resources = cloudinary.api.resources(
                    type='upload',
                    max_results=500
                )
            
            photos = resources.get('resources', [])
            total_photos = len(photos)
            self.stdout.write(self.style.SUCCESS(f"✓ Found {total_photos} photos in Cloudinary\n"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error fetching from Cloudinary: {str(e)}"))
            return
        
        # Sync photos to database
        synced = 0
        skipped = 0
        errors = 0
        
        for idx, photo_data in enumerate(photos, 1):
            public_id = photo_data['public_id']
            cloudinary_url = photo_data['secure_url']
            
            self.stdout.write(f"[{idx}/{total_photos}] {public_id}")
            self.stdout.write(f"  URL: {cloudinary_url}")
            
            # Check if photo already exists by checking if URL contains the public_id
            if Photo.objects.filter(image__contains=public_id).exists():
                self.stdout.write(self.style.WARNING(f"  ⏭️  Already exists, skipping"))
                skipped += 1
                continue
            
            try:
                # Create photo object
                photo = Photo.objects.create(
                    event=event,
                    image=cloudinary_url,
                    uploaded_at=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created database entry"))
                synced += 1
                
                # Face detection (optional)
                if not skip_face_detection:
                    self.stdout.write(f"  🔍 Running face detection...")
                    try:
                        from deepface import DeepFace
                        import numpy as np
                        
                        # Download image
                        response = requests.get(cloudinary_url)
                        img = Image.open(BytesIO(response.content))
                        img_array = np.array(img)
                        
                        # Detect faces with multiple backends
                        backends = ['retinaface', 'mtcnn', 'opencv', 'ssd']
                        faces_detected = False
                        
                        for backend in backends:
                            try:
                                face_objs = DeepFace.extract_faces(
                                    img_path=img_array,
                                    detector_backend=backend,
                                    enforce_detection=False
                                )
                                
                                if face_objs and len(face_objs) > 0:
                                    face_count = len(face_objs)
                                    photo.face_count = face_count
                                    photo.has_faces = True
                                    photo.save()
                                    self.stdout.write(self.style.SUCCESS(f"  👤 Detected {face_count} face(s) using {backend}"))
                                    faces_detected = True
                                    break
                            except Exception:
                                continue
                        
                        if not faces_detected:
                            self.stdout.write(self.style.WARNING(f"  ⚠️  No faces detected"))
                            
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠️  Face detection failed: {str(e)}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {str(e)}"))
                errors += 1
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ Sync Complete!"))
        self.stdout.write(f"Total in Cloudinary: {total_photos}")
        self.stdout.write(f"Synced to Database: {synced}")
        self.stdout.write(f"Skipped (already exists): {skipped}")
        self.stdout.write(f"Errors: {errors}")
        self.stdout.write("="*60)
        self.stdout.write(f"\n🎉 Photos are now visible at:")
        self.stdout.write(f"   https://hackotsava-images.onrender.com/events/{event_slug}/")
