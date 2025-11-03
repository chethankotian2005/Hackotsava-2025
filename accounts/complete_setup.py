"""
Complete setup and debug endpoint for production deployment
Visit /complete-setup/ to initialize everything
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from events.models import Event, Photo
import cloudinary
import cloudinary.api
from decouple import config
from datetime import datetime

def complete_setup(request):
    """Complete production setup - creates admin, event, and syncs photos"""
    
    output = []
    output.append("<html><head><title>Hackotsava Setup</title>")
    output.append("<style>")
    output.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }")
    output.append("h1 { color: #6c5ce7; } h2 { color: #0984e3; margin-top: 30px; }")
    output.append(".success { color: #00b894; } .error { color: #d63031; } .warning { color: #fdcb6e; }")
    output.append(".box { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
    output.append("pre { background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto; }")
    output.append("ul { line-height: 1.8; } .step { font-weight: bold; color: #6c5ce7; }")
    output.append("</style></head><body>")
    output.append("<h1>🚀 Hackotsava 2025 - Complete Setup</h1>")
    output.append("<p>Setting up your production environment...</p>")
    
    try:
        User = get_user_model()
        
        # STEP 1: Create Admin User
        output.append("<div class='box'>")
        output.append("<h2 class='step'>Step 1: Admin User Setup</h2>")
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hackotsava.com',
                'is_staff': True,
                'is_superuser': True,
                'role': 'ADMIN',
                'is_active': True
            }
        )
        
        if admin_created:
            admin_user.set_password('Kotian@2005')
            admin_user.save()
            output.append("<p class='success'>✅ Admin user created successfully!</p>")
        else:
            # Update existing admin
            admin_user.email = 'admin@hackotsava.com'
            admin_user.role = 'ADMIN'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.set_password('Kotian@2005')
            admin_user.save()
            output.append("<p class='success'>✅ Admin user updated!</p>")
        
        output.append(f"<ul><li><strong>Username:</strong> admin</li>")
        output.append(f"<li><strong>Password:</strong> Kotian@2005</li>")
        output.append(f"<li><strong>Email:</strong> {admin_user.email}</li>")
        output.append(f"<li><strong>Role:</strong> {admin_user.role}</li></ul>")
        output.append("</div>")
        
        # STEP 2: Create Event
        output.append("<div class='box'>")
        output.append("<h2 class='step'>Step 2: Event Setup</h2>")
        event, event_created = Event.objects.get_or_create(
            slug='hackotsava-2025',
            defaults={
                'name': 'Hackotsava 2025',
                'description': 'Hackotsava 2025 - Annual Tech Fest. Find your photos using AI-powered facial recognition!',
                'event_date': datetime(2025, 11, 3).date(),
                'location': 'College Campus',
                'is_public': True,
                'created_by': admin_user
            }
        )
        
        if event_created:
            output.append("<p class='success'>✅ Event created successfully!</p>")
        else:
            output.append("<p class='success'>✅ Event already exists!</p>")
        
        output.append(f"<ul><li><strong>Name:</strong> {event.name}</li>")
        output.append(f"<li><strong>Slug:</strong> {event.slug}</li>")
        output.append(f"<li><strong>Date:</strong> {event.event_date}</li>")
        output.append(f"<li><strong>Status:</strong> {'Public' if event.is_public else 'Private'}</li></ul>")
        output.append("</div>")
        
        # STEP 3: Sync Cloudinary Photos
        output.append("<div class='box'>")
        output.append("<h2 class='step'>Step 3: Cloudinary Photo Sync</h2>")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=config('CLOUDINARY_CLOUD_NAME'),
            api_key=config('CLOUDINARY_API_KEY'),
            api_secret=config('CLOUDINARY_API_SECRET')
        )
        
        output.append("<p>📡 Fetching photos from Cloudinary...</p>")
        
        # Fetch all photos from Cloudinary root
        resources = cloudinary.api.resources(
            type='upload',
            max_results=500
        )
        
        cloudinary_photos = resources.get('resources', [])
        total_cloudinary = len(cloudinary_photos)
        
        output.append(f"<p class='success'>✅ Found {total_cloudinary} photos in Cloudinary</p>")
        
        # Sync to database
        synced = 0
        skipped = 0
        errors = 0
        
        output.append("<p>🔄 Syncing to database...</p>")
        output.append("<ul>")
        
        for idx, photo_data in enumerate(cloudinary_photos, 1):
            public_id = photo_data['public_id']
            cloudinary_url = photo_data['secure_url']
            
            # Check if already exists
            if Photo.objects.filter(image__contains=public_id).exists():
                skipped += 1
                if idx <= 5:  # Show first 5
                    output.append(f"<li class='warning'>⏭️ [{idx}/{total_cloudinary}] {public_id} - Already exists</li>")
                continue
            
            try:
                # Create photo
                photo = Photo.objects.create(
                    event=event,
                    image=cloudinary_url
                )
                synced += 1
                if idx <= 5:  # Show first 5
                    output.append(f"<li class='success'>✅ [{idx}/{total_cloudinary}] {public_id} - Created</li>")
            except Exception as e:
                errors += 1
                if idx <= 5:
                    output.append(f"<li class='error'>❌ [{idx}/{total_cloudinary}] {public_id} - Error: {str(e)}</li>")
        
        if total_cloudinary > 5:
            output.append(f"<li>... processing {total_cloudinary - 5} more photos ...</li>")
        
        output.append("</ul>")
        
        output.append(f"<p class='success'><strong>📊 Sync Summary:</strong></p>")
        output.append(f"<ul>")
        output.append(f"<li>Total in Cloudinary: {total_cloudinary}</li>")
        output.append(f"<li>Newly Synced: {synced}</li>")
        output.append(f"<li>Already Existed: {skipped}</li>")
        output.append(f"<li>Errors: {errors}</li>")
        output.append(f"<li><strong>Total in Database Now: {Photo.objects.filter(event=event).count()}</strong></li>")
        output.append(f"</ul>")
        output.append("</div>")
        
        # STEP 4: Database Status
        output.append("<div class='box'>")
        output.append("<h2 class='step'>Step 4: Database Status</h2>")
        total_users = User.objects.count()
        total_events = Event.objects.count()
        total_photos = Photo.objects.count()
        
        output.append(f"<ul>")
        output.append(f"<li>👥 Total Users: {total_users}</li>")
        output.append(f"<li>📅 Total Events: {total_events}</li>")
        output.append(f"<li>📸 Total Photos: {total_photos}</li>")
        output.append(f"</ul>")
        output.append("</div>")
        
        # SUCCESS - Next Steps
        output.append("<div class='box' style='background: #d5f4e6;'>")
        output.append("<h2 class='success'>🎉 Setup Complete!</h2>")
        output.append("<p><strong>Your Hackotsava 2025 webapp is now fully configured and ready to use!</strong></p>")
        output.append("<h3>🔗 Quick Links:</h3>")
        output.append("<ul>")
        output.append(f"<li><a href='/events/{event.slug}/' target='_blank'><strong>📸 View Event Photos</strong></a> - See all {Photo.objects.filter(event=event).count()} photos</li>")
        output.append(f"<li><a href='/accounts/login/' target='_blank'><strong>🔐 Login as Admin</strong></a> - Username: admin, Password: Kotian@2005</li>")
        output.append(f"<li><a href='/dashboard/' target='_blank'><strong>📊 Admin Dashboard</strong></a> - Manage events and upload new photos</li>")
        output.append(f"<li><a href='/manage/event/{event.slug}/upload-photos/' target='_blank'><strong>⬆️ Upload More Photos</strong></a> - Add new event photos</li>")
        output.append(f"<li><a href='/analytics/' target='_blank'><strong>📈 Analytics</strong></a> - View usage statistics</li>")
        output.append("</ul>")
        
        output.append("<h3>✨ Features Available:</h3>")
        output.append("<ul>")
        output.append("<li>✅ AI-Powered Facial Recognition Search</li>")
        output.append("<li>✅ Bulk Photo Upload (up to 20MB per photo)</li>")
        output.append("<li>✅ Automatic Face Detection</li>")
        output.append("<li>✅ User Registration & Authentication</li>")
        output.append("<li>✅ Photo Download</li>")
        output.append("<li>✅ Admin Dashboard & Analytics</li>")
        output.append("<li>✅ Cloudinary Cloud Storage</li>")
        output.append("<li>✅ Responsive Design</li>")
        output.append("</ul>")
        
        output.append("<h3>📝 Admin Credentials:</h3>")
        output.append("<pre>Username: admin\nPassword: Kotian@2005\nRole: ADMIN</pre>")
        
        output.append("<p style='margin-top: 20px;'><strong>⚠️ Security Note:</strong> For production use, please change the admin password after first login and consider removing this setup endpoint.</p>")
        output.append("</div>")
        
    except Exception as e:
        output.append("<div class='box' style='background: #ffe0e0;'>")
        output.append(f"<h2 class='error'>❌ Setup Error</h2>")
        output.append(f"<p class='error'>{str(e)}</p>")
        import traceback
        output.append(f"<pre>{traceback.format_exc()}</pre>")
        output.append("</div>")
    
    output.append("</body></html>")
    
    return HttpResponse('\n'.join(output))
