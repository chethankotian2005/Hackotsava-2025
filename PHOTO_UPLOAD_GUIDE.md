# 📸 Manual Photo Upload Guide

## Method 1: Using Python Script (RECOMMENDED)

### Step 1: Prepare Your Photos
1. Create a folder with your photos (e.g., `photos_to_upload`)
2. Put all event photos in that folder

### Step 2: Run the Upload Script
```bash
python manual_upload_photos.py photos_to_upload
```

The script will:
- ✅ Upload photos to Cloudinary automatically
- ✅ Create database entries for each photo
- ✅ Run face detection on each photo
- ✅ Show progress and results

### Output Example:
```
============================================================
📸 Starting upload of 10 photos
Event: Hackotsava 2025
Folder: photos_to_upload
============================================================

[1/10] IMG_001.jpg
  ✅ Uploaded to Cloudinary
  📍 URL: https://res.cloudinary.com/.../event_photos/2025/11/03/IMG_001.jpg
  👤 Detected 3 face(s)

[2/10] IMG_002.jpg
  ✅ Uploaded to Cloudinary
  📍 URL: https://res.cloudinary.com/.../event_photos/2025/11/03/IMG_002.jpg
  👤 Detected 5 face(s)
...
```

---

## Method 2: Direct Cloudinary Upload (Manual)

### Cloudinary Folder Structure:
```
event_photos/
  └── 2025/
      └── 11/
          └── 03/
              ├── photo1.jpg
              ├── photo2.jpg
              └── photo3.jpg
```

### Steps:

#### 1. Login to Cloudinary
- Go to: https://cloudinary.com/console
- Use your Cloudinary credentials

#### 2. Upload Photos
- Click "Media Library" in sidebar
- Click "Upload" button
- Select your photos
- **IMPORTANT**: Set folder to `event_photos/2025/11/03/`

#### 3. Get Photo URLs
After upload, click each photo and copy the URL. It will look like:
```
https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/event_photos/2025/11/03/photo.jpg
```

#### 4. Create Database Entries
You'll need to run this in Django shell or create entries via admin panel.

**Problem with this method**: Photos won't have face detection unless you manually trigger it.

---

## Method 3: Django Admin Panel

### Step 1: Access Admin Panel
```
https://hackotsava-images.onrender.com/admin/
```

Login with:
- Username: `admin`
- Password: `Kotian@2005`

### Step 2: Add Photos Manually
1. Click "Photos" in Events section
2. Click "Add Photo +"
3. Fill in:
   - Event: Select "Hackotsava 2025"
   - Image: Upload file
   - Uploaded by: Select admin user
4. Click "Save"

### Step 3: Trigger Face Processing
Photos added this way need manual face processing. Run in Django shell:
```python
from events.models import Photo
from events.face_utils import process_photo_faces

# Process all unprocessed photos
for photo in Photo.objects.filter(faces_processed=False):
    process_photo_faces(photo)
```

---

## Cloudinary Configuration Details

Your photos are stored in Cloudinary with this structure:

**Path Format**: `event_photos/%Y/%m/%d/filename.jpg`

**Example Paths**:
- `event_photos/2025/11/03/photo1.jpg`
- `event_photos/2025/11/03/photo2.jpg`
- `event_photos/2025/11/04/photo3.jpg`

**Thumbnails**: `event_photos/thumbnails/%Y/%m/%d/filename.jpg`

**Full URL Format**:
```
https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/event_photos/2025/11/03/photo.jpg
```

---

## Troubleshooting

### Script Method Issues:

**"No module named django"**
```bash
pip install -r requirements.txt
```

**"Event 'hackotsava-2025' not found"**
```bash
# List available events
python manage.py shell
>>> from events.models import Event
>>> for e in Event.objects.all():
...     print(e.slug, e.name)
```

**"Cloudinary credentials not set"**
- Check `.env` file has:
  ```
  CLOUDINARY_CLOUD_NAME=your_cloud_name
  CLOUDINARY_API_KEY=your_api_key
  CLOUDINARY_API_SECRET=your_api_secret
  ```

### Direct Cloudinary Upload Issues:

**Photos not showing in webapp**
- Photos uploaded directly to Cloudinary won't appear until you create database entries
- Use Method 1 (Python script) to handle both automatically

**Wrong folder**
- Make sure you upload to `event_photos/YYYY/MM/DD/` format
- The app expects photos in dated folders

---

## Verification

After uploading photos, verify they appear:

1. Visit event page:
   ```
   https://hackotsava-images.onrender.com/events/hackotsava-2025/
   ```

2. Check photo count in admin dashboard:
   ```
   https://hackotsava-images.onrender.com/admin/
   ```
   Click "Dashboard" → should show total photos

3. Try face search:
   - Go to homepage
   - Upload a selfie
   - Select the event
   - Click "Find My Photos"

---

## Recommendation

**USE METHOD 1 (Python Script)** because it:
- ✅ Handles Cloudinary upload automatically
- ✅ Creates database entries
- ✅ Runs face detection
- ✅ Shows progress and errors
- ✅ Is the easiest and most reliable

Just put your photos in a folder and run:
```bash
python manual_upload_photos.py photos_to_upload
```

That's it! 🎉
