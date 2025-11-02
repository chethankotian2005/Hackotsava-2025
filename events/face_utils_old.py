"""
Face Recognition Utility Functions for Hackotsava 2025
Uses face_recognition library and OpenCV for face detection and matching
"""

# Try to import face_recognition, fall back to mock mode if not available
try:
    import face_recognition
    import cv2
    import numpy as np
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("WARNING: face_recognition not available. Running in MOCK mode.")
    print("Install face_recognition for full functionality. See INSTALL_WINDOWS.md")

from PIL import Image
import io
from django.conf import settings
from django.core.files.base import ContentFile


def detect_faces_in_image(image_path, url_hash=None):
    """
    Detect all faces in an image and return their encodings and locations.
    
    Args:
        image_path: Path to the image file or file object
        url_hash: Optional hash string for consistent encoding generation
        
    Returns:
        list of tuples: [(encoding, location), ...]
        where encoding is a 128-d face encoding
        and location is (top, right, bottom, left) coordinates
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Mock mode: Generate consistent fake face data for testing UI
        import random
        import numpy as np
        from PIL import Image
        import hashlib
        
        # Use url_hash if provided, otherwise try to hash image content
        if url_hash:
            seed = int(url_hash[:8], 16)
        else:
            # Try to get image content to create consistent encodings
            try:
                if hasattr(image_path, 'read'):
                    image_path.seek(0)
                    img = Image.open(image_path)
                    image_bytes = image_path.read()
                    image_path.seek(0)
                else:
                    img = Image.open(image_path)
                    with open(image_path, 'rb') as f:
                        image_bytes = f.read()
                
                # Create a hash of the image to use as seed (same image = same faces)
                image_hash = hashlib.md5(image_bytes).hexdigest()
                seed = int(image_hash[:8], 16)
            except Exception as e:
                # If we can't read the image, use a default encoding
                print(f"Warning: Could not read image for mock face detection: {e}")
                seed = 0
        
        # Set seed for consistent encoding
        np.random.seed(seed)
        random.seed(seed)
        
        # Determine number of faces
        try:
            if hasattr(image_path, 'read'):
                image_path.seek(0)
                img = Image.open(image_path)
                image_path.seek(0)
            else:
                img = Image.open(image_path)
            
            width, height = img.size
            total_pixels = width * height
            
            # Small images (< 1MP) likely selfies - return 1 face
            # Larger images likely event photos - return 1-2 faces
            if total_pixels < 1000000:  # Less than 1 megapixel
                num_faces = 1
            else:
                num_faces = random.randint(1, 2)
        except:
            num_faces = 1
        
        faces = []
        
        for i in range(num_faces):
            # Generate consistent 128-d encoding based on image hash
            # CRITICAL: Use randn() instead of rand() for normal distribution
            # Real face encodings are normalized with mean~0, std~0.1
            fake_encoding = np.random.randn(128) * 0.1  # Mean 0, std 0.1
            # Normalize to unit length (like real face encodings)
            fake_encoding = fake_encoding / np.linalg.norm(fake_encoding)
            
            # Generate random face location (top, right, bottom, left)
            fake_location = (
                random.randint(50, 200),   # top
                random.randint(300, 500),  # right
                random.randint(250, 400),  # bottom
                random.randint(100, 250)   # left
            )
            faces.append((fake_encoding, fake_location))
        
        # Reset random seed to avoid affecting other random operations
        np.random.seed(None)
        random.seed(None)
        
        return faces
    
    try:
        # Load image
        if hasattr(image_path, 'read'):
            # It's a file object
            image = face_recognition.load_image_file(image_path)
        else:
            # It's a file path
            image = face_recognition.load_image_file(image_path)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(image, model='hog')
        
        # Get face encodings for detected faces
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        # Combine encodings with their locations
        results = list(zip(face_encodings, face_locations))
        
        return results
    
    except Exception as e:
        print(f"Error detecting faces: {str(e)}")
        return []


def encoding_to_string(encoding):
    """
    Convert numpy array encoding to comma-separated string for database storage.
    
    Args:
        encoding: numpy array of face encoding (128 dimensions)
        
    Returns:
        str: comma-separated string of encoding values
    """
    # Works in both real and mock mode
    return ','.join(str(x) for x in encoding)


def string_to_encoding(encoding_string):
    """
    Convert stored string encoding back to numpy array.
    
    Args:
        encoding_string: comma-separated string of encoding values
        
    Returns:
        numpy array: face encoding
    """
    import numpy as np
    
    if not encoding_string or encoding_string.strip() == '':
        return np.array([])
    
    try:
        return np.array([float(x) for x in encoding_string.split(',')])
    except:
        return np.array([])



def compare_faces(known_encodings, face_encoding, tolerance=None):
    """
    Compare a face encoding against known face encodings.
    
    Args:
        known_encodings: list of known face encodings (as strings or arrays)
        face_encoding: face encoding to compare (as string or array)
        tolerance: how much distance between faces to consider a match (default: 0.6)
        
    Returns:
        tuple: (matches, face_distances)
        matches: list of boolean values indicating matches
        face_distances: list of distance values for each comparison
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Mock mode: Calculate actual Euclidean distance between encodings
        import numpy as np
        
        num_known = len(known_encodings)
        if num_known == 0:
            return [], []
        
        if tolerance is None:
            tolerance = 0.6
        
        # Convert to numpy arrays if needed
        if isinstance(face_encoding, str):
            face_encoding = string_to_encoding(face_encoding)
        
        known_encoding_arrays = []
        for enc in known_encodings:
            if isinstance(enc, str):
                known_encoding_arrays.append(string_to_encoding(enc))
            else:
                known_encoding_arrays.append(enc)
        
        # Calculate Euclidean distance for each known encoding
        face_distances = []
        for known_enc in known_encoding_arrays:
            if len(known_enc) == 0 or len(face_encoding) == 0:
                face_distances.append(1.0)  # Maximum distance
            else:
                distance = np.linalg.norm(known_enc - face_encoding)
                face_distances.append(float(distance))
        
        # Determine matches based on tolerance
        matches = [distance <= tolerance for distance in face_distances]
        
        return matches, face_distances
    
    if tolerance is None:
        tolerance = settings.FACE_RECOGNITION_TOLERANCE
    
    # Convert to numpy arrays if needed
    if isinstance(face_encoding, str):
        face_encoding = string_to_encoding(face_encoding)
    
    known_encoding_arrays = []
    for enc in known_encodings:
        if isinstance(enc, str):
            known_encoding_arrays.append(string_to_encoding(enc))
        else:
            known_encoding_arrays.append(enc)
    
    # Compare faces
    matches = face_recognition.compare_faces(
        known_encoding_arrays,
        face_encoding,
        tolerance=tolerance
    )
    
    # Get face distances
    face_distances = face_recognition.face_distance(
        known_encoding_arrays,
        face_encoding
    )
    
    return matches, face_distances


def find_matching_photos(selfie_encoding, event):
    """
    Find all photos in an event that contain a face matching the selfie.
    
    Args:
        selfie_encoding: face encoding from user's selfie
        event: Event object to search in
        
    Returns:
        list of tuples: [(photo, confidence), ...]
        sorted by confidence (lower distance = higher confidence)
    """
    from events.models import FaceEncoding, Photo
    
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
        stored_encoding = face_enc.get_encoding_array()
        matches, distances = compare_faces([stored_encoding], selfie_encoding)
        
        if matches[0]:
            # Calculate confidence (0-100, where 100 is perfect match)
            confidence = max(0, min(100, (1 - distances[0]) * 100))
            matching_photos.append((face_enc.photo, confidence, distances[0]))
            seen_photos.add(face_enc.photo.id)
    
    # Sort by distance (lower is better)
    matching_photos.sort(key=lambda x: x[2])
    
    # Return photo and confidence only
    return [(photo, conf) for photo, conf, _ in matching_photos]


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


def draw_face_boxes(image_path, face_locations, output_path=None):
    """
    Draw bounding boxes around detected faces (for debugging/visualization).
    
    Args:
        image_path: path to the image
        face_locations: list of (top, right, bottom, left) tuples
        output_path: optional path to save the annotated image
        
    Returns:
        numpy array: image with face boxes drawn
    """
    # Load image
    image = cv2.imread(str(image_path))
    
    # Draw rectangles around faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(image, (left, top), (right, bottom), (139, 92, 246), 2)
    
    # Save if output path provided
    if output_path:
        cv2.imwrite(output_path, image)
    
    return image


def process_photo_faces(photo_obj):
    """
    Process a photo to detect and store face encodings.
    
    Args:
        photo_obj: Photo model instance
        
    Returns:
        int: number of faces detected and processed
    """
    from events.models import FaceEncoding
    import requests
    from io import BytesIO
    import hashlib
    
    try:
        # For Cloudinary storage, download the image temporarily
        if hasattr(photo_obj.image, 'url'):
            # Download image from Cloudinary URL
            image_url = photo_obj.image.url
            response = requests.get(image_url)
            image_file = BytesIO(response.content)
            
            # Store URL hash for consistent encoding generation
            url_hash = hashlib.md5(image_url.encode()).hexdigest()
        else:
            # Local storage - use path
            image_file = photo_obj.image.path
            # Use file path as hash source
            url_hash = hashlib.md5(str(photo_obj.image.path).encode()).hexdigest()
        
        # Detect faces in the photo - pass url_hash for consistency
        faces_data = detect_faces_in_image(image_file, url_hash=url_hash)
        
        # Create FaceEncoding objects for each detected face
        for encoding, location in faces_data:
            FaceEncoding.objects.create(
                photo=photo_obj,
                encoding=encoding_to_string(encoding),
                top=location[0],
                right=location[1],
                bottom=location[2],
                left=location[3]
            )
        
        # Update photo metadata
        photo_obj.faces_processed = True
        photo_obj.face_count = len(faces_data)
        photo_obj.save()
        
        return len(faces_data)
    
    except Exception as e:
        print(f"Error processing photo faces: {str(e)}")
        import traceback
        traceback.print_exc()
        photo_obj.faces_processed = True
        photo_obj.face_count = 0
        photo_obj.save()
        return 0


def validate_image_file(file):
    """
    Validate uploaded image file.
    
    Args:
        file: uploaded file object
        
    Returns:
        tuple: (is_valid, error_message)
    """
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
        return False, "Invalid image file"
