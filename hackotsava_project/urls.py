"""
URL Configuration for Hackotsava 2025 Event Photo Finder
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts.init_admin import init_admin
from accounts.fix_admin_role import fix_admin_role
from accounts.check_admin import check_admin_status
from accounts.quick_fix_admin import quick_fix_admin
from accounts.sync_photos_view import sync_cloudinary_photos
from accounts.setup_event import setup_event
from accounts.complete_setup import complete_setup
from accounts.debug_db import debug_db

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('accounts/', include('accounts.urls')),
    # Complete setup endpoint - ONE-CLICK SETUP
    path('complete-setup/', complete_setup, name='complete_setup'),
    # Individual setup URLs
    path('setup-event/', setup_event, name='setup_event'),
    path('init-admin-secret-setup/', init_admin, name='init_admin'),
    path('fix-admin-role/', fix_admin_role, name='fix_admin_role'),
    path('check-admin-status/', check_admin_status, name='check_admin_status'),
    path('quick-fix-admin/', quick_fix_admin, name='quick_fix_admin'),
    # Cloudinary sync URL
    path('sync-cloudinary-photos/', sync_cloudinary_photos, name='sync_cloudinary_photos'),
    # Debug DB endpoint (safe for initial troubleshooting; remove in production)
    path('debug-db/', debug_db, name='debug_db'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'events.views.custom_404'
handler500 = 'events.views.custom_500'

# Customize admin site
admin.site.site_header = "Hackotsava 2025 Admin"
admin.site.site_title = "Hackotsava Admin Portal"
admin.site.index_title = "Welcome to Hackotsava 2025 Administration"
