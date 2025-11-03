"""
Quick endpoint to sync Cloudinary photos to database
Visit /sync-cloudinary-photos/ to sync photos
"""
from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO

def sync_cloudinary_photos(request):
    """Run the sync_cloudinary management command via web"""
    
    output_html = "<h1>🔄 Cloudinary Photo Sync</h1><hr>"
    
    try:
        # Capture command output
        out = StringIO()
        
        # Run the management command
        call_command('sync_cloudinary', '--no-face-detection', stdout=out)
        
        # Get the output
        command_output = out.getvalue()
        
        # Convert to HTML
        output_html += "<h2>✅ Sync Complete!</h2>"
        output_html += "<pre style='background: #f4f4f4; padding: 20px; border-radius: 5px;'>"
        output_html += command_output
        output_html += "</pre>"
        
        output_html += "<hr>"
        output_html += "<p><a href='/events/hackotsava-2025/'>View Photos</a></p>"
        output_html += "<p><a href='/admin/dashboard/'>Admin Dashboard</a></p>"
        
    except Exception as e:
        output_html += f"<h2>❌ Error</h2>"
        output_html += f"<p style='color: red;'>{str(e)}</p>"
        output_html += f"<pre style='background: #ffeeee; padding: 20px;'>{type(e).__name__}: {str(e)}</pre>"
    
    return HttpResponse(output_html)
