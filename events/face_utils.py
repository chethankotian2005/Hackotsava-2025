"""
Face Recognition Utility Functions for Hackotsava 2025
Uses DeepFace library for face detection and matching
"""

import os
import io
import hashlib
import numpy as np
import requests
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile

# Lazy loading: Don't import DeepFace until actually needed
_deepface_loaded = False
_deepface = None
_cv2 = None

def _ensure_deepface():
    """Lazy load DeepFace only when needed to save memory"""
    global _deepface_loaded, _deepface, _cv2
    if not _deepface_loaded:
        try:
            from deepface import DeepFace
            import cv2
            _deepface = DeepFace
            _cv2 = cv2
            _deepface_loaded = True
            print("✓ DeepFace library loaded successfully")
            print("⭐ Using ArcFace model with multi-detector fallback")
            print("⭐ Threshold: 1.2 (very lenient - finds similar face structures)")
            print("⭐ Handles: glasses, sunglasses, different angles, lighting")
            print("⭐ Preprocessing: CLAHE + brightness normalization for selfies")
        except ImportError:
            print("WARNING: DeepFace not available.")
            print("Install it with: pip install deepface tf-keras")
            raise
    return _deepface, _cv2

DEEPFACE_AVAILABLE = True  # Assume available unless import fails


def preprocess_image_for_matching(img_path, is_selfie=False):
    """
    Preprocess image to improve face recognition accuracy.
    Applies aggressive preprocessing for selfies to match event photo quality.
    
    Args:
        img_path: Path to image file
        is_selfie: If True, applies extra preprocessing for selfie images
        
    Returns:
        Path to preprocessed image file
    """
    import tempfile
    
    # Lazy load cv2 only when needed
    _, cv2 = _ensure_deepface()
    
    try:
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            return img_path
        
        # Convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to standard size for consistency
        height, width = img.shape[:2]
        max_dim = 1024
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        if is_selfie:
            # Extra preprocessing for selfies
            print("  🔧 Applying selfie preprocessing (CLAHE, brightness normalization)...")
            
            # Apply CLAHE for better contrast
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            img = cv2.merge([l, a, b])
            img = cv2.cvtColor(img, cv2.COLOR_LAB2RGB)
        
        # Save preprocessed image to temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(temp_fd)
        cv2.imwrite(temp_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return temp_path
        
    except Exception as e:
        print(f"  ⚠️ Preprocessing failed: {e}, using original image")
        return img_path


def detect_faces_in_image(image_path, url_hash=None, is_selfie=False):
    """
    Detect all faces in an image and return their encodings and locations.
    Uses multi-detector fallback: retinaface → mtcnn → opencv → ssd
    
    Args:
        image_path: Path to the image file (string path)
        url_hash: Optional hash string for consistent encoding generation
        is_selfie: If True, applies extra preprocessing for selfie matching
        
    Returns:
        list of tuples: [(encoding, location), ...]
        where encoding is a 512-d face embedding
        and location is (top, right, bottom, left) coordinates
    """
    # Lazy load DeepFace only when actually needed
    try:
        DeepFace, cv2 = _ensure_deepface()
    except ImportError:
        # Fallback mock mode
        return _mock_detect_faces(image_path, url_hash)
    
    try:
        # Ensure we have a file path
        if hasattr(image_path, 'read'):
            # It's a file object - save to temp file
            import tempfile
            image_path.seek(0)
            img_data = image_path.read()
            image_path.seek(0)
            
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            with os.fdopen(temp_fd, 'wb') as tmp:
                tmp.write(img_data)
            
            img_path = temp_path
            cleanup_temp = True
        else:
            # It's already a file path
            img_path = image_path
            cleanup_temp = False
        
        # 🔥 Apply preprocessing for better matching
        preprocessed_path = preprocess_image_for_matching(img_path, is_selfie=is_selfie)
        if preprocessed_path != img_path:
            # Use preprocessed image, clean it up later
            img_path = preprocessed_path
            cleanup_temp = True
        
        faces = []
        
        try:
            # 🔥 MULTI-DETECTOR FALLBACK for maximum detection success
            detector_backends = ['retinaface', 'mtcnn', 'opencv', 'ssd']
            face_objs = None
            successful_detector = None
            
            for detector in detector_backends:
                try:
                    print(f"  🔍 Trying {detector} detector...")
                    face_objs = DeepFace.extract_faces(
                        img_path=img_path,
                        detector_backend=detector,
                        enforce_detection=False,     # Don't fail if no face found
                        align=True                   # ⭐ CRITICAL: Align faces for consistency
                    )
                    
                    if face_objs and len(face_objs) > 0:
                        successful_detector = detector
                        print(f"  ✅ {detector} detected {len(face_objs)} face(s)")
                        break  # Success! Use this detector
                        
                except Exception as e:
                    print(f"  ⚠️ {detector} failed: {str(e)}")
                    continue
            
            if not face_objs:
                print("  ❌ All detectors failed to find faces")
                return []
            
            # Load the image to get face regions (cv2 already loaded via _ensure_deepface)
            img = cv2.imread(img_path)
            if img is None:
                print(f"❌ Error: Could not load image from {img_path}")
                return []
            
            img_height, img_width = img.shape[:2]
            
            for idx, face_obj in enumerate(face_objs):
                # Get face region (pixel coordinates)
                region = face_obj['facial_area']
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                
                # Convert to (top, right, bottom, left) with padding
                padding = 20  # Add padding for better recognition
                top = max(0, int(y) - padding)
                right = min(img_width, int(x + w) + padding)
                bottom = min(img_height, int(y + h) + padding)
                left = max(0, int(x) - padding)
                
                location = (int(y), int(x + w), int(y + h), int(x))  # Original location without padding
                
                # Extract the face region with padding
                face_img = img[top:bottom, left:right]
                
                if face_img.size == 0:
                    print(f"  ⚠️ Face #{idx+1}: empty face region")
                    continue
                
                # Save face to temp file
                import tempfile
                temp_face_fd, temp_face_path = tempfile.mkstemp(suffix='.jpg')
                cv2.imwrite(temp_face_path, face_img)
                os.close(temp_face_fd)
                
                try:
                    # Get embedding using ArcFace (512 dimensions, best accuracy 95%+)
                    embedding_objs = DeepFace.represent(
                        img_path=temp_face_path,
                        model_name='ArcFace',      # ⭐ Best model - 95%+ accuracy
                        detector_backend='skip',   # We already detected the face
                        enforce_detection=False,
                        align=True                 # ⭐ CRITICAL: Align for consistency
                    )
                    
                    if embedding_objs and len(embedding_objs) > 0:
                        embedding = np.array(embedding_objs[0]['embedding'])
                        
                        # ⭐ CRITICAL: L2 normalization for proper cosine similarity
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = embedding / norm
                        
                        # Verify embedding is valid
                        if not np.any(np.isnan(embedding)) and not np.all(embedding == 0):
                            faces.append((embedding, location))
                            print(f"    ✓ Face #{idx+1}: embedding extracted (shape={embedding.shape}, norm={np.linalg.norm(embedding):.4f})")
                        else:
                            print(f"    ⚠️ Face #{idx+1}: invalid embedding (NaN or zeros)")
                    else:
                        print(f"    ⚠️ Face #{idx+1}: no embedding returned")
                        
                except Exception as e:
                    print(f"    ❌ Face #{idx+1}: embedding extraction failed - {str(e)}")
                finally:
                    # Clean up temp face file
                    if os.path.exists(temp_face_path):
                        os.unlink(temp_face_path)
        
        finally:
            # Clean up temp file if we created one
            if cleanup_temp and os.path.exists(img_path):
                os.unlink(img_path)
        
        print(f"  📊 Successfully extracted {len(faces)} valid embedding(s)")
        return faces
    
    except Exception as e:
        print(f"❌ Error detecting faces with DeepFace: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def _mock_detect_faces(image_path, url_hash=None):
    """Mock face detection for when DeepFace is not available"""
    import random
    
    # Use url_hash if provided
    if url_hash:
        seed = int(url_hash[:8], 16)
    else:
        seed = 0
    
    np.random.seed(seed)
    random.seed(seed)
    
    # Generate 1 fake face
    fake_encoding = np.random.randn(512) * 0.1  # Match ArcFace dimensions (512-D)
    fake_encoding = fake_encoding / np.linalg.norm(fake_encoding)
    
    fake_location = (50, 350, 250, 150)
    
    np.random.seed(None)
    random.seed(None)
    
    return [(fake_encoding, fake_location)]


def encoding_to_string(encoding):
    """
    Convert numpy array encoding to comma-separated string for database storage.
    
    Args:
        encoding: numpy array of face encoding (512 dimensions for Facenet512)
        
    Returns:
        str: comma-separated string of encoding values
    """
    if encoding is None or len(encoding) == 0:
        return ""
    
    # Convert to list and then to comma-separated string
    return ','.join(map(str, encoding.tolist()))


def string_to_encoding(encoding_string):
    """
    Convert comma-separated string back to numpy array encoding.
    
    Args:
        encoding_string: comma-separated string of encoding values
        
    Returns:
        numpy array: face encoding
    """
    if not encoding_string or encoding_string.strip() == "":
        return np.array([])
    
    try:
        # Split string and convert to floats
        values = [float(x) for x in encoding_string.split(',')]
        return np.array(values)
    except (ValueError, AttributeError) as e:
        print(f"Error converting encoding string: {e}")
        return np.array([])


def compare_faces(known_encodings, face_encoding, tolerance=0.6):
    """
    Compare a face encoding against known encodings.
    
    Args:
        known_encodings: list of known face encodings
        face_encoding: encoding to compare
        tolerance: how much distance between faces to consider it a match (lower = more strict)
        
    Returns:
        list of booleans: True for matches, False for non-matches
    """
    if len(known_encodings) == 0:
        return []
    
    # Calculate Euclidean distance between face encoding and all known encodings
    # DeepFace uses cosine similarity, but Euclidean works well with normalized vectors
    distances = []
    for known_encoding in known_encodings:
        if len(known_encoding) == 0 or len(face_encoding) == 0:
            distances.append(float('inf'))
            continue
        
        # Euclidean distance
        distance = np.linalg.norm(known_encoding - face_encoding)
        distances.append(distance)
    
    # Return list of booleans indicating matches (distance <= tolerance)
    matches = [distance <= tolerance for distance in distances]
    
    return matches, distances


def process_photo_faces(photo):
    """
    Process a photo to detect and store face encodings.
    
    Args:
        photo: Photo model instance with uploaded image
        
    Returns:
        int: number of faces detected
    """
    from .models import FaceEncoding
    
    try:
        # Get image URL
        image_url = photo.image.url
        
        # Create hash from URL for consistent encoding
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # Download image and save to temp file (DeepFace needs real file path)
        import tempfile
        response = requests.get(image_url)
        
        # Create temp file with proper extension
        temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        with os.fdopen(temp_fd, 'wb') as tmp:
            tmp.write(response.content)
        
        try:
            # Detect faces - pass file path instead of BytesIO
            faces = detect_faces_in_image(temp_path, url_hash=url_hash)
            
            # Store each face encoding
            for encoding, location in faces:
                FaceEncoding.objects.create(
                    photo=photo,
                    encoding=encoding_to_string(encoding),
                    top=location[0],
                    right=location[1],
                    bottom=location[2],
                    left=location[3]
                )
            
            # Update photo face count
            photo.face_count = len(faces)
            photo.faces_processed = True
            photo.save()
            
            return len(faces)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        print(f"Error processing photo faces: {str(e)}")
        import traceback
        traceback.print_exc()
        photo.faces_processed = True  # Mark as processed even if failed
        photo.save()
        return 0


def validate_image_file(file):
    """
    Validate uploaded image file.
    
    Args:
        file: uploaded file object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    from django.conf import settings
    
    # Check file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        return False, "Only JPEG, PNG, and WebP images are allowed"
    
    # Try to open as image
    try:
        img = Image.open(file)
        img.verify()
        return True, None
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def create_thumbnail(image_path, size=(300, 300)):
    """
    Create a thumbnail version of an image.
    
    Args:
        image_path: path to the original image
        size: tuple of (width, height) for thumbnail
        
    Returns:
        ContentFile object containing the thumbnail
    """
    try:
        # Open image
        if hasattr(image_path, 'read'):
            img = Image.open(image_path)
        else:
            img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)
        
        return ContentFile(thumb_io.getvalue())
    
    except Exception as e:
        print(f"Error creating thumbnail: {str(e)}")
        return None


def find_matching_photos(selfie_encoding, event, tolerance=0.6):
    """
    Find all photos in an event that contain a face matching the selfie.
    
    Args:
        selfie_encoding: face encoding from user's selfie
        event: Event object to search in
        tolerance: matching tolerance (lower = stricter)
        
    Returns:
        list of tuples: [(photo, confidence), ...]
        sorted by confidence (lower distance = higher confidence)
    """
    from .models import FaceEncoding, Photo
    
    # Get all face encodings for photos in this event
    face_encodings = FaceEncoding.objects.filter(
        photo__event=event
    ).select_related('photo')
    
    matching_photos = []
    seen_photos = set()
    
    for face_enc in face_encodings:
        # Skip if we've already matched this photo
        if face_enc.photo.id in seen_photos:
            continue
        
        # Compare faces
        stored_encoding = string_to_encoding(face_enc.encoding)
        matches, distances = compare_faces([stored_encoding], selfie_encoding, tolerance=tolerance)
        
        if matches[0]:
            # Calculate confidence (0-100, where 100 is perfect match)
            confidence = max(0, min(100, (1 - distances[0]) * 100))
            matching_photos.append((face_enc.photo, confidence, distances[0]))
            seen_photos.add(face_enc.photo.id)
    
    # Sort by distance (lower is better)
    matching_photos.sort(key=lambda x: x[2])
    
    # Return photo and confidence only
    return [(photo, conf) for photo, conf, _ in matching_photos]
