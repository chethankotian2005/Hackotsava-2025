"""
Views for Events App - Complete implementation with face recognition
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.db.models import Count, Q, Max
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from functools import wraps
import tempfile
import os

from .models import Event, Photo, FaceEncoding, SearchHistory
from .forms import EventForm, BulkPhotoUploadForm, SelfieUploadForm
from .face_utils import (
    detect_faces_in_image,
    process_photo_faces,
    create_thumbnail,
    validate_image_file,
    string_to_encoding,
    compare_faces,
    find_matching_photos,
)


# Decorator for admin-only views
def admin_required(view_func):
    """Decorator to restrict view to admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============== PUBLIC VIEWS ==============

def home(request):
    """
    Homepage with hero section and featured events
    """
    recent_events = Event.objects.filter(is_public=True)[:6]
    total_events = Event.objects.filter(is_public=True).count()
    total_photos = Photo.objects.filter(event__is_public=True).count()
    
    context = {
        'page_title': 'Hackotsava 2025 - Event Photo Finder',
        'recent_events': recent_events,
        'total_events': total_events,
        'total_photos': total_photos,
    }
    return render(request, 'events/home.html', context)


def event_list(request):
    """
    List all public events with search and filtering
    """
    events = Event.objects.filter(is_public=True).annotate(
        photo_count=Count('photos')
    )
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Events - Hackotsava 2025',
        'events': events_page,
        'search_query': search_query,
    }
    return render(request, 'events/event_list.html', context)


def browse_photos(request):
    """
    Browse all photos from all public events
    """
    # Get all public events or all events if user is admin
    if request.user.is_authenticated and request.user.is_admin():
        photos = Photo.objects.select_related('event').order_by('-uploaded_at')
    else:
        photos = Photo.objects.filter(event__is_public=True).select_related('event').order_by('-uploaded_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        photos = photos.filter(
            Q(event__name__icontains=search_query) |
            Q(event__location__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(photos, 24)
    page_number = request.GET.get('page')
    photos_page = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Browse Photos - Hackotsava 2025',
        'photos': photos_page,
        'search_query': search_query,
        'total_photos': photos.count(),
    }
    return render(request, 'events/browse_photos.html', context)


@require_http_methods(["POST"])
def find_my_photos(request):
    """
    AJAX endpoint to find photos containing the user's face
    """
    from django.http import JsonResponse
    import json
    
    try:
        print("\n" + "="*60)
        print("🔍 FIND MY PHOTOS - DEBUG")
        print("="*60)
        
        if 'selfie' not in request.FILES:
            print("❌ No selfie in request")
            return JsonResponse({'success': False, 'error': 'No selfie uploaded'})
        
        selfie = request.FILES['selfie']
        # 🔥 LENIENT TOLERANCE: Find similar face structures even with:
        # - Glasses/sunglasses
        # - Different lighting/angles
        # - Accessories (hats, etc.)
        # Testing shows distances 0.88-1.28 for same person in different conditions
        tolerance = 1.2  # Very lenient for similar face structures
        print(f"📸 Selfie uploaded: {selfie.name} ({selfie.size} bytes)")
        print(f"🎯 Using lenient threshold for similar face structures:")
        print(f"   - Excellent match: distance < 0.60")
        print(f"   - Good match: distance < 0.85")
        print(f"   - Similar face: distance < 1.20")
        
        # Detect face in selfie with preprocessing
        faces = detect_faces_in_image(selfie, is_selfie=True)  # Apply selfie preprocessing
        print(f"👤 Faces detected in selfie: {len(faces)}")
        
        if not faces:
            print("❌ No faces detected")
            return JsonResponse({
                'success': False,
                'error': 'No face detected in your selfie. Please upload a clear photo of your face.'
            })
        
        if len(faces) > 1:
            print("❌ Multiple faces detected")
            return JsonResponse({
                'success': False,
                'error': 'Multiple faces detected. Please upload a photo with only your face.'
            })
        
        # Get the face encoding
        selfie_encoding = faces[0][0]
        print(f"✅ Selfie encoding shape: {selfie_encoding.shape if hasattr(selfie_encoding, 'shape') else len(selfie_encoding)}")
        
        # Find matching photos across all public events (or all events if admin)
        if request.user.is_authenticated and request.user.is_admin():
            all_photos = Photo.objects.filter(faces_processed=True)
        else:
            all_photos = Photo.objects.filter(event__is_public=True, faces_processed=True)
        
        print(f"📊 Total photos to check: {all_photos.count()}")
        
        matches = []
        checked_count = 0
        all_distances = []
        
        for photo in all_photos:
            # Get all face encodings for this photo
            face_encodings = photo.face_encodings.all()
            
            if not face_encodings.exists():
                continue
            
            for face_encoding in face_encodings:
                checked_count += 1
                # Compare faces
                encoding_array = string_to_encoding(face_encoding.encoding)
                
                # Verify encoding is valid
                if len(encoding_array) == 0:
                    print(f"  ⚠️ Photo #{photo.id}: empty encoding, skipping")
                    continue
                
                is_match, distance = compare_faces([encoding_array], selfie_encoding, tolerance)
                
                all_distances.append(distance[0])
                
                if is_match[0]:
                    # ⭐ CATEGORIZE BY CONFIDENCE (lenient for similar faces)
                    dist = distance[0]
                    if dist < 0.60:
                        quality = "Excellent match"
                        confidence_pct = 90
                    elif dist < 0.85:
                        quality = "Good match"
                        confidence_pct = 75
                    else:  # dist < 1.20
                        quality = "Similar face"
                        confidence_pct = 60
                    
                    confidence = 1 - dist  # Convert distance to confidence
                    print(f"  ✅ MATCH! Photo #{photo.id}, distance: {dist:.4f}, quality: {quality}, confidence: {confidence_pct}%")
                    matches.append({
                        'photo_id': str(photo.id),
                        'photo_url': photo.image.url,
                        'download_url': reverse('download_photo', args=[photo.id]),
                        'confidence': float(confidence),
                        'confidence_pct': confidence_pct,
                        'quality': quality,
                        'distance': float(dist),
                        'event_name': photo.event.name
                    })
                    break  # Found a match in this photo, no need to check other faces
        
        if all_distances:
            import statistics
            print(f"  📏 Distance stats: min={min(all_distances):.4f}, max={max(all_distances):.4f}, avg={statistics.mean(all_distances):.4f}")
            print(f"  🎯 Current tolerance: {tolerance}")
            matches_count = sum(1 for d in all_distances if d <= tolerance)
            print(f"  💡 Distances below tolerance would match: {matches_count}")
            
            # Show top 10 closest distances for debugging
            sorted_distances = sorted(all_distances)[:10]
            print(f"  🔝 Top 10 closest distances: {[f'{d:.4f}' for d in sorted_distances]}")
            
            if matches_count == 0 and len(all_distances) > 0:
                closest = min(all_distances)
                suggested_tolerance = closest + 0.05
                print(f"  💡 Suggestion: No matches found. Closest distance was {closest:.4f}.")
                print(f"     Try tolerance >= {suggested_tolerance:.2f} to include closest match")
        
        print(f"\n📈 Results: Checked {checked_count} faces, found {len(matches)} matches")
        print("="*60 + "\n")
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Save search history if user is authenticated
        if request.user.is_authenticated and matches:
            # Get the first event from matches (or create a generic search history)
            first_match_event = Photo.objects.get(id=matches[0]['photo_id']).event
            SearchHistory.objects.create(
                user=request.user,
                event=first_match_event,
                matches_found=len(matches)
            )
        
        return JsonResponse({
            'success': True,
            'matches': matches,
            'total_searched': all_photos.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })


def event_detail(request, slug):
    """
    Event detail page with overview and stats
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check if event is public or user is admin
    if not event.is_public and not (request.user.is_authenticated and request.user.is_admin()):
        messages.error(request, 'This event is private.')
        return redirect('event_list')
    
    photo_count = event.get_photo_count()
    face_count = event.get_face_count()
    recent_photos = event.photos.all()[:12]
    
    context = {
        'page_title': f'{event.name} - Hackotsava 2025',
        'event': event,
        'photo_count': photo_count,
        'face_count': face_count,
        'recent_photos': recent_photos,
    }
    return render(request, 'events/event_detail.html', context)


def event_gallery(request, slug):
    """
    Full gallery view of event photos
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check permissions
    if not event.is_public and not (request.user.is_authenticated and request.user.is_admin()):
        messages.error(request, 'This event is private.')
        return redirect('event_list')
    
    photos = event.photos.all()
    
    # Pagination
    paginator = Paginator(photos, 24)
    page_number = request.GET.get('page')
    photos_page = paginator.get_page(page_number)
    
    context = {
        'page_title': f'{event.name} Gallery - Hackotsava 2025',
        'event': event,
        'photos': photos_page,
    }
    return render(request, 'events/gallery.html', context)


def search_faces(request, slug):
    """
    Search for photos containing user's face
    """
    event = get_object_or_404(Event, slug=slug)
    
    # Check permissions
    if not event.is_public and not (request.user.is_authenticated and request.user.is_admin()):
        messages.error(request, 'This event is private.')
        return redirect('event_list')
    
    matching_photos = []
    form = SelfieUploadForm()
    
    if request.method == 'POST':
        form = SelfieUploadForm(request.POST, request.FILES)
        if form.is_valid():
            selfie = request.FILES['selfie']
            tolerance = form.cleaned_data.get('tolerance', 0.6)
            
            # Validate image
            is_valid, error_msg = validate_image_file(selfie)
            if not is_valid:
                messages.error(request, error_msg)
            else:
                try:
                    # Detect face in selfie
                    faces = detect_faces_in_image(selfie)
                    
                    if not faces:
                        messages.warning(request, 'No face detected in the uploaded photo. Please upload a clear selfie.')
                    elif len(faces) > 1:
                        messages.warning(request, 'Multiple faces detected. Please upload a photo with only your face.')
                    else:
                        # Get the face encoding
                        selfie_encoding = faces[0][0]
                        
                        # Find matching photos
                        matching_photos = find_matching_photos(selfie_encoding, event)
                        
                        # Save search history
                        if request.user.is_authenticated:
                            SearchHistory.objects.create(
                                user=request.user,
                                event=event,
                                matches_found=len(matching_photos)
                            )
                        
                        if matching_photos:
                            messages.success(request, f'Found {len(matching_photos)} photos containing your face!')
                        else:
                            messages.info(request, 'No matching photos found. Try adjusting the tolerance or upload a different photo.')
                
                except Exception as e:
                    messages.error(request, f'Error processing image: {str(e)}')
    
    context = {
        'page_title': f'Search Photos - {event.name}',
        'event': event,
        'form': form,
        'matching_photos': matching_photos,
    }
    return render(request, 'events/search.html', context)


def download_photo(request, photo_id):
    """
    Download a single photo (always in JPEG format)
    """
    from PIL import Image
    from io import BytesIO
    
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check permissions
    if not photo.event.is_public and not (request.user.is_authenticated and request.user.is_admin()):
        raise Http404("Photo not found")
    
    try:
        # Open the image
        img = Image.open(photo.image)
        
        # Convert to RGB if necessary (handles PNG with transparency, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPEG to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95, optimize=True)
        buffer.seek(0)
        
        # Create response
        response = FileResponse(buffer, content_type='image/jpeg')
        
        # Generate filename (replace extension with .jpg)
        original_name = os.path.basename(photo.image.name)
        name_without_ext = os.path.splitext(original_name)[0]
        jpeg_filename = f"{name_without_ext}.jpg"
        
        response['Content-Disposition'] = f'attachment; filename="{jpeg_filename}"'
        return response
    except Exception as e:
        print(f"Error downloading photo: {e}")
        raise Http404("Photo file not found")


@require_http_methods(["POST"])
def download_all_photos(request):
    """
    Download multiple photos as a ZIP file (optimized for speed)
    """
    from io import BytesIO
    import zipfile
    import requests
    
    try:
        # Get photo IDs from POST request
        photo_ids = request.POST.getlist('photo_ids[]')
        
        print(f"📦 Download All Request - Received {len(photo_ids)} photo IDs")
        
        if not photo_ids:
            print("❌ No photo IDs provided in request")
            return HttpResponse("No photos selected for download", status=400)
        
        # Limit to prevent timeout (max 50 photos)
        if len(photo_ids) > 50:
            photo_ids = photo_ids[:50]
            print(f"⚠️ Limited to first 50 photos to prevent timeout")
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        
        print(f"🔧 Creating ZIP file...")
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:  # No compression for speed
            for idx, photo_id in enumerate(photo_ids, 1):
                try:
                    photo = Photo.objects.get(id=photo_id)
                    
                    # Check permissions
                    if not photo.event.is_public and not (request.user.is_authenticated and request.user.is_admin()):
                        continue
                    
                    # Get image URL
                    photo_url = str(photo.image.url)
                    
                    # Download image directly from Cloudinary
                    response = requests.get(photo_url, timeout=10)
                    if response.status_code == 200:
                        # Get original filename
                        original_name = os.path.basename(photo.image.name)
                        filename = f"{idx:03d}_{original_name}"
                        
                        # Add to ZIP without re-encoding
                        zip_file.writestr(filename, response.content)
                        print(f"  ✓ Added {idx}/{len(photo_ids)}: {filename[:50]}...")
                    else:
                        print(f"  ✗ Failed to download photo {photo_id}: HTTP {response.status_code}")
                    
                except Photo.DoesNotExist:
                    print(f"  ✗ Photo {photo_id} not found")
                    continue
                except requests.Timeout:
                    print(f"  ✗ Timeout downloading photo {photo_id}")
                    continue
                except Exception as e:
                    print(f"  ✗ Error processing photo {photo_id}: {e}")
                    continue
        
        # Prepare response
        zip_buffer.seek(0)
        print(f"✅ ZIP created successfully with {len(photo_ids)} photos")
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="hackotsava_photos.zip"'
        response['Content-Length'] = zip_buffer.tell()
        return response
        
    except Exception as e:
        print(f"❌ Error creating ZIP: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error creating ZIP file: {str(e)}", status=500)


# ============== ADMIN VIEWS ==============

@admin_required
def admin_dashboard(request):
    """
    Admin dashboard with statistics and recent activity
    """
    # Create default Hackotsava 2025 event if it doesn't exist
    from datetime import date
    default_event, created = Event.objects.get_or_create(
        slug='hackotsava-2025',
        defaults={
            'name': 'Hackotsava 2025',
            'description': 'A national level 30 hours hackathon',
            'event_date': date.today(),
            'location': 'Tech Campus',
            'created_by': request.user,
            'is_public': True
        }
    )
    
    total_events = Event.objects.count()
    total_photos = Photo.objects.count()
    total_faces = FaceEncoding.objects.count()
    total_searches = SearchHistory.objects.count()
    
    recent_events = Event.objects.all()[:5]
    recent_searches = SearchHistory.objects.select_related('user', 'event')[:10]
    
    # Photos pending face processing
    pending_photos = Photo.objects.filter(faces_processed=False).count()
    
    context = {
        'page_title': 'Admin Dashboard - Hackotsava 2025',
        'total_events': total_events,
        'total_photos': total_photos,
        'total_faces': total_faces,
        'total_searches': total_searches,
        'recent_events': recent_events,
        'recent_searches': recent_searches,
        'pending_photos': pending_photos,
    }
    return render(request, 'events/admin/dashboard.html', context)


@admin_required
def create_event(request):
    """
    Create a new event
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.name}" created successfully!')
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventForm()
    
    context = {
        'page_title': 'Create Event - Hackotsava 2025',
        'form': form,
    }
    return render(request, 'events/admin/event_form.html', context)


@admin_required
def edit_event(request, slug):
    """
    Edit an existing event
    """
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
    
    context = {
        'page_title': f'Edit {event.name} - Hackotsava 2025',
        'form': form,
        'event': event,
    }
    return render(request, 'events/admin/event_form.html', context)


@admin_required
def delete_event(request, slug):
    """
    Delete an event and all associated photos
    """
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f'Event "{event_name}" deleted successfully!')
        return redirect('event_list')
    
    context = {
        'page_title': f'Delete {event.name} - Hackotsava 2025',
        'event': event,
    }
    return render(request, 'events/admin/event_confirm_delete.html', context)


@admin_required
def upload_photos(request, slug):
    """
    Bulk upload photos to an event and process faces
    """
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        form = BulkPhotoUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('photos')
        
        if files:
            total_files = len(files)
            uploaded_count = 0
            error_count = 0
            
            print(f"\n{'='*60}")
            print(f"📸 Starting upload of {total_files} photos to Cloudinary...")
            print(f"{'='*60}\n")
            
            for index, file in enumerate(files, 1):
                print(f"[{index}/{total_files}] Uploading: {file.name} ({file.size / 1024 / 1024:.2f} MB)")
                
                # Validate each file
                is_valid, error_msg = validate_image_file(file)
                if not is_valid:
                    error_count += 1
                    print(f"  ❌ Validation failed: {error_msg}")
                    messages.warning(request, f'{file.name}: {error_msg}')
                    continue
                
                try:
                    # Create Photo object - Cloudinary handles upload automatically
                    photo = Photo.objects.create(
                        event=event,
                        image=file,
                        uploaded_by=request.user
                    )
                    
                    uploaded_count += 1
                    print(f"  ✅ Uploaded to Cloudinary!")
                    
                    # Process faces immediately (fast in MOCK mode)
                    try:
                        faces_count = process_photo_faces(photo)
                        print(f"  👤 Detected {faces_count} face(s) - Total progress: {uploaded_count}/{total_files}")
                    except Exception as face_error:
                        print(f"  ⚠️  Face processing failed: {str(face_error)}")
                        # Continue anyway, photo is uploaded
                
                except Exception as e:
                    error_count += 1
                    print(f"  ❌ Upload failed: {str(e)}")
                    messages.warning(request, f'{file.name}: Error - {str(e)}')
            
            print(f"\n{'='*60}")
            print(f"✅ Upload complete! Success: {uploaded_count}, Failed: {error_count}")
            print(f"{'='*60}\n")
            
            if uploaded_count > 0:
                messages.success(request, f'Successfully uploaded {uploaded_count} photos! Face detection will run in the background.')
            if error_count > 0:
                messages.warning(request, f'Failed to upload {error_count} files.')
            
            return redirect('event_detail', slug=event.slug)
    else:
        form = BulkPhotoUploadForm()
    
    context = {
        'page_title': f'Upload Photos - {event.name}',
        'event': event,
        'form': form,
    }
    return render(request, 'events/admin/upload_photos.html', context)


@admin_required
def delete_photo(request, photo_id):
    """
    Delete a single photo
    """
    photo = get_object_or_404(Photo, id=photo_id)
    event_slug = photo.event.slug
    
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('event_detail', slug=event_slug)
    
    context = {
        'page_title': 'Delete Photo - Hackotsava 2025',
        'photo': photo,
    }
    return render(request, 'events/admin/photo_confirm_delete.html', context)


@admin_required
def analytics(request):
    """
    Analytics and statistics page
    """
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    
    User = get_user_model()
    
    # Overall statistics
    total_events = Event.objects.count()
    total_photos = Photo.objects.count()
    total_faces = FaceEncoding.objects.count()
    total_searches = SearchHistory.objects.count()
    total_users = User.objects.count()
    
    # User statistics
    active_users_24h = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    active_users_7d = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Currently active users (logged in within last hour)
    active_now = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(hours=1)
    ).order_by('-last_login')[:20]
    
    # Events with most photos
    top_events = Event.objects.annotate(
        photo_count=Count('photos')
    ).order_by('-photo_count')[:10]
    
    # Calculate percentages for chart
    max_photos = top_events.first().photo_count if top_events.exists() else 1
    for event in top_events:
        event.percentage = (event.photo_count / max_photos * 100) if max_photos > 0 else 0
    
    # Recent search activity
    recent_searches = SearchHistory.objects.select_related('user', 'event').order_by('-searched_at')[:20]
    
    # User activity with enhanced details
    top_searchers = SearchHistory.objects.values(
        'user__username', 
        'user__email'
    ).annotate(
        search_count=Count('id'),
        total_matches=Sum('matches_found'),
        last_search=Max('searched_at')
    ).order_by('-search_count')[:15]
    
    context = {
        'page_title': 'Analytics - Hackotsava 2025',
        'total_events': total_events,
        'total_photos': total_photos,
        'total_faces': total_faces,
        'total_searches': total_searches,
        'total_users': total_users,
        'active_users_24h': active_users_24h,
        'active_users_7d': active_users_7d,
        'recent_users': recent_users,
        'active_now': active_now,
        'top_events': top_events,
        'recent_searches': recent_searches,
        'top_searchers': top_searchers,
    }
    return render(request, 'events/admin/analytics.html', context)


@admin_required
@require_http_methods(["POST"])
def delete_photo(request, photo_id):
    """
    Delete a single photo from database and Cloudinary
    """
    import cloudinary.uploader
    
    photo = get_object_or_404(Photo, id=photo_id)
    
    try:
        # Delete from Cloudinary
        if photo.image:
            try:
                # Extract public_id from Cloudinary URL
                url_parts = str(photo.image).split('/')
                if 'upload' in url_parts:
                    upload_index = url_parts.index('upload')
                    public_id_with_ext = '/'.join(url_parts[upload_index + 2:])
                    public_id = public_id_with_ext.rsplit('.', 1)[0]
                    
                    # Delete from Cloudinary
                    result = cloudinary.uploader.destroy(public_id)
                    if result.get('result') != 'ok':
                        messages.warning(request, f'Photo removed from database but Cloudinary deletion returned: {result.get("result")}')
            except Exception as e:
                messages.warning(request, f'Photo removed from database but Cloudinary deletion failed: {str(e)}')
        
        # Delete from database (cascade deletes FaceEncodings)
        event_id = photo.event.id
        photo.delete()
        
        messages.success(request, 'Photo deleted successfully!')
        
        # Return JSON response for AJAX or redirect for regular POST
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Photo deleted successfully'})
        else:
            return redirect('manage_event', event_id=event_id)
            
    except Exception as e:
        messages.error(request, f'Error deleting photo: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            return redirect('manage_event', event_id=event_id)


@admin_required
@require_http_methods(["POST"])
def bulk_delete_photos(request):
    """
    Delete multiple photos at once (admin only)
    """
    import cloudinary.uploader
    import json
    
    try:
        # Get photo IDs from request
        photo_ids = request.POST.getlist('photo_ids[]')
        
        if not photo_ids:
            return JsonResponse({'success': False, 'error': 'No photos selected'})
        
        deleted_count = 0
        failed_count = 0
        errors = []
        
        for photo_id in photo_ids:
            try:
                photo = Photo.objects.get(id=photo_id)
                
                # Delete from Cloudinary
                if photo.image:
                    try:
                        url_parts = str(photo.image).split('/')
                        if 'upload' in url_parts:
                            upload_index = url_parts.index('upload')
                            public_id_with_ext = '/'.join(url_parts[upload_index + 2:])
                            public_id = public_id_with_ext.rsplit('.', 1)[0]
                            cloudinary.uploader.destroy(public_id)
                    except Exception as e:
                        print(f"Cloudinary deletion failed for {photo_id}: {e}")
                
                # Delete from database
                photo.delete()
                deleted_count += 1
                
            except Photo.DoesNotExist:
                failed_count += 1
                errors.append(f"Photo {photo_id} not found")
            except Exception as e:
                failed_count += 1
                errors.append(f"Error deleting photo {photo_id}: {str(e)}")
        
        message = f"Successfully deleted {deleted_count} photo(s)"
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'deleted': deleted_count,
            'failed': failed_count,
            'errors': errors
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============== ERROR HANDLERS ==============

def custom_404(request, exception=None):
    """Custom 404 error page"""
    context = {
        'page_title': '404 - Page Not Found'
    }
    return render(request, 'errors/404.html', context, status=404)


def custom_500(request):
    """Custom 500 error page"""
    context = {
        'page_title': '500 - Server Error'
    }
    return render(request, 'errors/500.html', context, status=500)
