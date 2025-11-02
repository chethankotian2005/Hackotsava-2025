"""
Reset database for deployment - Clear all data and set admin password
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackotsava_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from events.models import Event, Photo, SearchHistory

User = get_user_model()

def reset_database():
    print("🗑️  Clearing database...")
    
    # Delete all search history
    searches = SearchHistory.objects.all()
    count = searches.count()
    searches.delete()
    print(f"   ✅ Deleted {count} search records")
    
    # Delete all photos
    photos = Photo.objects.all()
    count = photos.count()
    photos.delete()
    print(f"   ✅ Deleted {count} photos")
    
    # Delete all events
    events = Event.objects.all()
    count = events.count()
    events.delete()
    print(f"   ✅ Deleted {count} events")
    
    # Delete all non-superuser users
    users = User.objects.filter(is_superuser=False)
    count = users.count()
    users.delete()
    print(f"   ✅ Deleted {count} regular users")
    
    print("\n🔐 Updating admin password...")
    
    # Update or create admin user
    admin_user = User.objects.filter(email='admin@hackotsava.com').first()
    
    if admin_user:
        admin_user.set_password('Kotian@2005')
        admin_user.role = 'admin'
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print(f"   ✅ Updated admin password")
        print(f"   📧 Email: admin@hackotsava.com")
        print(f"   🔑 Password: Kotian@2005")
    else:
        admin_user = User.objects.create_superuser(
            email='admin@hackotsava.com',
            password='Kotian@2005'
        )
        admin_user.first_name = 'Admin'
        admin_user.role = 'admin'
        admin_user.save()
        print(f"   ✅ Created new admin user")
        print(f"   📧 Email: admin@hackotsava.com")
        print(f"   🔑 Password: Kotian@2005")
    
    print("\n✨ Database reset complete!")
    print("\n⚠️  Note: Photos stored on Cloudinary need to be deleted manually from Cloudinary dashboard")

if __name__ == '__main__':
    reset_database()
