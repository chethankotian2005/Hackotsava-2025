# 📸 Admin Photo Upload Guide - Hackotsava 2025

## ✅ YES! You Can Upload Photos as Admin

The web app has a **fully functional photo upload system** that allows you to add new photos at any time.

---

## 🚀 How to Upload New Photos

### Step 1: Access the Admin Dashboard
1. Go to: **https://hackotsava-images.onrender.com/dashboard/**
2. Login with your admin credentials:
   - Username: `admin`
   - Password: `Kotian@2005`

### Step 2: Click "Upload Photos" Button
- You'll see a prominent **"Upload Photos"** button on the dashboard
- Or directly visit: **https://hackotsava-images.onrender.com/manage/event/hackotsava-2025/upload-photos/**

### Step 3: Upload Your Photos
- **Drag & Drop** photos into the upload zone, OR
- **Click** to select multiple photos from your computer
- Supported formats: JPG, PNG, WEBP
- Maximum size: **20MB per photo**
- You can upload **multiple photos at once**

### Step 4: Automatic Processing
✨ The system will automatically:
1. Upload photos to Cloudinary (cloud storage)
2. Create database entries
3. Run face detection on each photo
4. Generate face encodings for searching
5. Show you the progress and results

---

## 📊 Features

### ✅ What Happens Automatically:
- ✓ Photos uploaded to Cloudinary
- ✓ Face detection (counts how many faces in each photo)
- ✓ Face encoding for search matching
- ✓ Photos immediately visible on the website
- ✓ Progress tracking during upload
- ✓ Success/error status for each file

### 📁 Upload Limits:
- Max file size: **20MB** per photo
- No limit on number of photos per upload
- Supported formats: JPG, PNG, WEBP

### 🔍 Face Detection:
- Uses DeepFace AI with multiple detection backends
- Tries: RetinaFace → MTCNN → OpenCV → SSD
- Automatically generates face encodings
- Shows face count for each uploaded photo

---

## 🎯 After Upload

Once uploaded, your photos will:
1. Appear on the event page: `/events/hackotsava-2025/`
2. Be searchable via facial recognition
3. Be downloadable by users who match
4. Show in admin analytics

---

## 🔗 Quick Links

| Action | URL |
|--------|-----|
| **Admin Dashboard** | https://hackotsava-images.onrender.com/dashboard/ |
| **Upload Photos** | https://hackotsava-images.onrender.com/manage/event/hackotsava-2025/upload-photos/ |
| **View Event Photos** | https://hackotsava-images.onrender.com/events/hackotsava-2025/ |
| **Analytics** | https://hackotsava-images.onrender.com/analytics/ |

---

## 💡 Tips for Best Results

1. **High-Quality Photos**: Upload clear, well-lit photos for better face detection
2. **Face Visibility**: Ensure faces are clearly visible (not too far, not covered)
3. **Batch Upload**: You can select and upload 20-50 photos at once
4. **Monitor Progress**: Watch the progress bar to see upload status
5. **Check Results**: After upload, visit the event page to verify photos are visible

---

## 🆘 Troubleshooting

### Upload Not Working?
1. **Check Admin Access**: Visit `/quick-fix-admin/` first
2. **Check File Size**: Ensure files are under 20MB
3. **Check Format**: Only JPG, PNG, WEBP supported
4. **Clear Browser Cache**: Refresh the page (Ctrl+F5)

### Photos Not Appearing?
1. Wait a few seconds after upload
2. Refresh the event page
3. Check dashboard for "pending photos" count
4. Photos should appear immediately after successful upload

### Face Detection Failed?
- Photos will still be uploaded and visible
- Face detection might fail for:
  - Very small faces
  - Poor lighting
  - Faces turned away
  - Low-resolution images
- Users can still browse and download photos

---

## 🎉 Summary

**Yes, you can continuously upload new photos through the web app!**

The system is designed for ongoing photo uploads. Just:
1. Login as admin
2. Go to Dashboard → Upload Photos
3. Select your new photos
4. Upload & done!

No need for manual scripts or command-line tools. The web interface handles everything automatically! 🚀
