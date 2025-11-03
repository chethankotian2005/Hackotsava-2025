"""
Quick setup to create the Hackotsava 2025 event
Visit /setup-event/ to create the event
"""
from django.http import HttpResponse
from django.utils import timezone
from events.models import Event
from datetime import datetime

def setup_event(request):
    """Create the Hackotsava 2025 event if it doesn't exist"""
    
    output_html = "<h1>🎪 Event Setup</h1><hr>"
    
    try:
        # Check if event exists
        event, created = Event.objects.get_or_create(
            slug='hackotsava-2025',
            defaults={
                'name': 'Hackotsava 2025',
                'description': 'Hackotsava 2025 - Annual Tech Fest',
                'event_date': datetime(2025, 11, 3).date(),
                'location': 'College Campus',
                'is_public': True
            }
        )
        
        if created:
            output_html += "<h2>✅ Event Created Successfully!</h2>"
            output_html += f"<p><strong>Name:</strong> {event.name}</p>"
            output_html += f"<p><strong>Slug:</strong> {event.slug}</p>"
            output_html += f"<p><strong>Date:</strong> {event.event_date}</p>"
            output_html += f"<p><strong>Status:</strong> {'Public' if event.is_public else 'Private'}</p>"
        else:
            output_html += "<h2>ℹ️ Event Already Exists</h2>"
            output_html += f"<p><strong>Name:</strong> {event.name}</p>"
            output_html += f"<p><strong>Slug:</strong> {event.slug}</p>"
            output_html += f"<p><strong>Date:</strong> {event.event_date}</p>"
            output_html += f"<p><strong>Photos:</strong> {event.photos.count()}</p>"
        
        output_html += "<hr>"
        output_html += "<h3>Next Steps:</h3>"
        output_html += "<ol>"
        output_html += "<li>✅ Event is ready!</li>"
        output_html += "<li><a href='/sync-cloudinary-photos/'>Sync Cloudinary Photos</a></li>"
        output_html += "<li><a href='/events/hackotsava-2025/'>View Event Page</a></li>"
        output_html += "<li><a href='/dashboard/'>Admin Dashboard</a></li>"
        output_html += "</ol>"
        
    except Exception as e:
        output_html += f"<h2>❌ Error</h2>"
        output_html += f"<p style='color: red;'>{str(e)}</p>"
        import traceback
        output_html += f"<pre style='background: #ffeeee; padding: 20px;'>{traceback.format_exc()}</pre>"
    
    return HttpResponse(output_html)
