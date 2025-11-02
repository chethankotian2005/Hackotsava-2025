"""
Management command to delete all photos from database and Cloudinary
"""
from django.core.management.base import BaseCommand
from events.models import Photo
import cloudinary.uploader


class Command(BaseCommand):
    help = 'Delete all photos from database and Cloudinary'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        total = photos.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No photos to delete.'))
            return
        
        self.stdout.write(f'Found {total} photos to delete.')
        confirm = input(f'Are you sure you want to delete all {total} photos? (yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING('Deletion cancelled.'))
            return
        
        deleted_count = 0
        failed_count = 0
        
        for i, photo in enumerate(photos, 1):
            try:
                self.stdout.write(f'[{i}/{total}] Deleting photo {photo.id}...')
                
                # Get Cloudinary public_id from the image URL
                if photo.image:
                    try:
                        # Extract public_id from Cloudinary URL
                        # Format: https://res.cloudinary.com/<cloud>/image/upload/v<version>/<public_id>.<ext>
                        url_parts = str(photo.image).split('/')
                        if 'upload' in url_parts:
                            upload_index = url_parts.index('upload')
                            # Get everything after 'upload/v<version>/'
                            public_id_with_ext = '/'.join(url_parts[upload_index + 2:])
                            # Remove file extension
                            public_id = public_id_with_ext.rsplit('.', 1)[0]
                            
                            # Delete from Cloudinary
                            result = cloudinary.uploader.destroy(public_id)
                            if result.get('result') == 'ok':
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted from Cloudinary'))
                            else:
                                self.stdout.write(self.style.WARNING(f'  ⚠ Cloudinary delete status: {result.get("result")}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Could not delete from Cloudinary: {e}'))
                
                # Delete from database (this also deletes related FaceEncodings due to CASCADE)
                photo.delete()
                deleted_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted from database'))
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Deleted {deleted_count} photos'))
        if failed_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠ Failed to delete {failed_count} photos'))
