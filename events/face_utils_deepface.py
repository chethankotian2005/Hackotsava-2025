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

try:
    from deepface import DeepFace
    import cv2
    DEEPFACE_AVAILABLE = True
    print("✓ DeepFace library loaded successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("WARNING: DeepFace not available.")
    print("Install it with: pip install deepface tf-keras")


def detect_faces_in_image(image_path, url_hash=None):
    """
    Detect all faces in an image and return their encodings and locations.
    
    Args:
        image_path: Path to the image file or file object
        url_hash: Optional hash string for consistent encoding generation
        
    Returns:
        list of tuples: [(encoding, location), ...]
        where encoding is a 128-d face embedding
        and location is (top, right, bottom, left) coordinates
    """
    if not DEEPFACE_AVAILABLE:
        # Fallback mock mode
        return _mock_detect_faces(image_path, url_hash)
    
    try:
        # Save to temp file if it's a file object
        temp_path = None
        if hasattr(image_path, 'read'):
            import tempfile
            image_path.seek(0)
            img_data = image_path.read()
            image_path.seek(0)
            
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
            with os.fdopen(temp_fd, 'wb') as tmp:
                tmp.write(img_data)
            
            img_path = temp_path
        else:
            img_path = image_path
        
        # Detect and extract faces using DeepFace
        # Use VGG-Face model for embeddings (returns 2622-d vector)
        # We'll use Facenet512 which gives 512-d vectors (more similar to face_recognition's 128-d)
        faces = []
        
        try:
            # Extract faces with DeepFace
            face_objs = DeepFace.extract_faces(
                img_path=img_path,
                detector_backend='opencv',  # Faster than mtcnn
                enforce_detection=False,     # Don't fail if no face found
                align=True                   # Align faces for better recognition
            )
            
            if not face_objs:
                return []
            
            # Load the image to get actual pixel coordinates
            img = cv2.imread(img_path)
            img_height, img_width = img.shape[:2]
            
            for face_obj in face_objs:
                # Get face region (normalized coordinates)
                region = face_obj['facial_area']
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                
                # Convert to actual pixel coordinates (top, right, bottom, left)
                top = int(y)
                right = int(x + w)
                bottom = int(y + h)
                left = int(x)
                
                location = (top, right, bottom, left)
                
                # Get embedding for this face
                # Extract the face region
                face_img = img[top:bottom, left:right]
                
                # Save face to temp file
                temp_face_fd, temp_face_path = tempfile.mkstemp(suffix='.jpg')
                cv2.imwrite(temp_face_path, face_img)
                os.close(temp_face_fd)
                
                try:
                    # Get embedding using Facenet512 (512 dimensions)
                    embedding_objs = DeepFace.represent(
                        img_path=temp_face_path,
                        model_name='Facenet512',  # 512-d embeddings
                        detector_backend='skip',   # We already detected the face
                        enforce_detection=False
                    )
                    
                    if embedding_objs and len(embedding_objs) > 0:
                        embedding = np.array(embedding_objs[0]['embedding'])
                        # Normalize to unit length (like face_recognition does)
                        embedding = embedding / np.linalg.norm(embedding)
                        faces.append((embedding, location))
                finally:
                    # Clean up temp face file
                    if os.path.exists(temp_face_path):
                        os.unlink(temp_face_path)
        
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return faces
    
    except Exception as e:
        print(f"Error detecting faces with DeepFace: {str(e)}")
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
    fake_encoding = np.random.randn(512) * 0.1  # Match Facenet512 dimensions
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
        # Download image from Cloudinary
        import io
        import requests
        
        # Get image URL
        image_url = photo.image.url
        
        # Download image
        response = requests.get(image_url)
        image_data = io.BytesIO(response.content)
        
        # Create hash from URL for consistent encoding
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # Detect faces
        faces = detect_faces_in_image(image_data, url_hash=url_hash)
        
        # Store each face encoding
        for encoding, location in faces:
            FaceEncoding.objects.create(
                photo=photo,
                encoding=encoding_to_string(encoding),
                location_top=location[0],
                location_right=location[1],
                location_bottom=location[2],
                location_left=location[3]
            )
        
        # Update photo face count
        photo.face_count = len(faces)
        photo.faces_processed = True
        photo.save()
        
        return len(faces)
    
    except Exception as e:
        print(f"Error processing photo faces: {str(e)}")
        import traceback
        traceback.print_exc()
        photo.faces_processed = True  # Mark as processed even if failed
        photo.save()
        return 0
