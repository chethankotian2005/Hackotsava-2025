"""
URL Configuration for Events App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('browse-photos/', views.browse_photos, name='browse_photos'),
    path('find-my-photos/', views.find_my_photos, name='find_my_photos'),
    path('events/', views.event_list, name='event_list'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/gallery/', views.event_gallery, name='event_gallery'),
    path('event/<slug:slug>/search/', views.search_faces, name='search_faces'),
    
    # Admin pages (require admin role)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/event/create/', views.create_event, name='create_event'),
    path('manage/event/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('manage/event/<slug:slug>/delete/', views.delete_event, name='delete_event'),
    path('manage/event/<slug:slug>/upload-photos/', views.upload_photos, name='upload_photos'),
    path('manage/photo/<uuid:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('manage/photos/bulk-delete/', views.bulk_delete_photos, name='bulk_delete_photos'),
    path('analytics/', views.analytics, name='analytics'),
    
    # Download
    path('photo/<uuid:photo_id>/download/', views.download_photo, name='download_photo'),
    path('photos/download-all/', views.download_all_photos, name='download_all_photos'),
    
    # Error pages
    path('404/', views.custom_404, name='custom_404'),
    path('500/', views.custom_500, name='custom_500'),
]
