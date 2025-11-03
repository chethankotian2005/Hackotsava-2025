"""
Debug endpoint to check database status
Visit /debug-db/ to see what's in the production database
"""
from django.http import HttpResponse
from events.models import Event, Photo
from django.contrib.auth import get_user_model


def debug_db(request):
    """Check what's in the database"""
    
    output_html = "<h1>🔍 Database Debug</h1><hr>"
    
    try:
        User = get_user_model()
        
        # Check users
        users = User.objects.all()
        output_html += f"<h2>👥 Users: {users.count()}</h2>"
        output_html += "<ul>"
        for user in users:
            output_html += f"<li>{user.username} - Role: {getattr(user, 'role', 'N/A')} - Staff: {user.is_staff} - Superuser: {user.is_superuser}</li>"
        output_html += "</ul>"
        
        # Check events
        events = Event.objects.all()
        output_html += f"<h2>📅 Events: {events.count()}</h2>"
        output_html += "<ul>"
        for event in events:
            photo_count = event.photos.count()
            output_html += f"<li><strong>{event.name}</strong> (slug: {event.slug}) - Photos: {photo_count} - Public: {event.is_public}</li>"
        output_html += "</ul>"
        
        # Check photos
        photos = Photo.objects.all()
        output_html += f"<h2>📸 Photos: {photos.count()}</h2>"
        if photos.exists():
            output_html += "<ul>"
            for photo in photos[:20]:  # Show first 20
                try:
                    image_url = photo.image.url
                except Exception:
                    image_url = str(photo.image)
                output_html += f"<li>Event: {photo.event.name} - Image: {image_url[:200]} - Faces: {photo.face_count} - Processed: {photo.faces_processed}</li>"
            output_html += "</ul>"
            if photos.count() > 20:
                output_html += f"<p><em>... and {photos.count() - 20} more photos</em></p>"
        else:
            output_html += "<p style='color: red;'>⚠️ No photos in database!</p>"
        
        output_html += "<hr>"
        output_html += "<h3>🔗 Quick Links:</h3>"
        output_html += "<ul>"
        output_html += "<li><a href='/setup-event/'>Setup Event</a></li>"
        output_html += "<li><a href='/sync-cloudinary-photos/'>Sync Cloudinary Photos</a></li>"
        if events.exists():
            output_html += f"<li><a href='/events/{events.first().slug}/'>View First Event</a></li>"
        output_html += "<li><a href='/dashboard/'>Admin Dashboard</a></li>"
        output_html += "</ul>"
        
    except Exception as e:
        output_html += f"<h2>❌ Error</h2>"
        output_html += f"<p style='color: red;'>{str(e)}</p>"
        import traceback
        output_html += f"<pre style='background: #ffeeee; padding: 20px;'>{traceback.format_exc()}</pre>"
    
    return HttpResponse(output_html)
