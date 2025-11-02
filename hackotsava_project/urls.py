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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('accounts/', include('accounts.urls')),
    # One-time admin setup URLs
    path('init-admin-secret-setup/', init_admin, name='init_admin'),
    path('fix-admin-role/', fix_admin_role, name='fix_admin_role'),
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
