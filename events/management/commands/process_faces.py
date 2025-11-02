"""
Management command to process faces in uploaded photos
"""
from django.core.management.base import BaseCommand
from events.models import Photo
from events.face_utils import process_photo_faces


class Command(BaseCommand):
    help = 'Process faces in all unprocessed photos'

    def handle(self, *args, **options):
        unprocessed = Photo.objects.filter(faces_processed=False)
        total = unprocessed.count()
        
        self.stdout.write(f'\nFound {total} unprocessed photos\n')
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No photos to process!'))
            return
        
        processed = 0
        for index, photo in enumerate(unprocessed, 1):
            self.stdout.write(f'[{index}/{total}] Processing photo #{photo.id}...')
            try:
                faces_count = process_photo_faces(photo)
                self.stdout.write(self.style.SUCCESS(f'  ✅ Detected {faces_count} face(s)'))
                processed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Processed {processed}/{total} photos'))
