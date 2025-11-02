# 🚀 Hackotsava 2025 - Render Deployment Guide

## Prerequisites
- GitHub account
- Render account (free tier available)
- Cloudinary account for image storage

## Step 1: Prepare for Deployment

### 1.1 Reset Database and Set Admin Password
Run the reset script to clear all data and set the admin password:

```bash
python reset_for_deployment.py
```

This will:
- ✅ Delete all face searches, photos, and events
- ✅ Delete all regular users
- ✅ Set admin password to `Kotian@2005`
- ✅ Admin email: `admin@hackotsava.com`

### 1.2 Clean Up Cloudinary
Manually delete all photos from your Cloudinary dashboard:
1. Go to https://cloudinary.com/console
2. Navigate to Media Library
3. Select and delete all uploaded photos

## Step 2: Push to GitHub

### 2.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### 2.2 Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., `hackotsava-2025`)
3. Push your code:

```bash
git remote add origin https://github.com/YOUR_USERNAME/hackotsava-2025.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render

### 3.1 Create New Web Service
1. Go to https://dashboard.render.com/
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select the `hackotsava-2025` repository

### 3.2 Configure Service Settings
- **Name**: `hackotsava-2025`
- **Region**: Choose closest to your location
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn hackotsava_project.wsgi:application`
- **Instance Type**: Free

### 3.3 Add Environment Variables
Click "Advanced" → "Add Environment Variable" and add these:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Generate new key | Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` | IMPORTANT: Never True in production |
| `DATABASE_URL` | (Auto-added by Render) | When you add PostgreSQL database |
| `CLOUDINARY_CLOUD_NAME` | Your cloud name | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | Your API key | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | Your API secret | From Cloudinary dashboard |
| `ALLOWED_HOSTS` | `.onrender.com` | Your Render domain |
| `PYTHON_VERSION` | `3.11.0` | Matches runtime.txt |

### 3.4 Add PostgreSQL Database
1. In Render dashboard, click "New" → "PostgreSQL"
2. Name: `hackotsava-db`
3. Database: `hackotsava`
4. User: (auto-generated)
5. Region: Same as web service
6. Instance Type: Free
7. Click "Create Database"

### 3.5 Link Database to Web Service
1. Go back to your web service settings
2. In Environment Variables, find `DATABASE_URL`
3. It should be automatically linked to your PostgreSQL database
4. If not, copy the Internal Database URL from PostgreSQL service

## Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Render will automatically:
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start the application

## Step 5: Create Admin User on Production

After deployment, go to the Render Shell:

1. Click your web service → "Shell"
2. Run:
```bash
python manage.py createsuperuser
```
- Email: `admin@hackotsava.com`
- Full name: `Admin`
- Password: `Kotian@2005`
- Confirm password: `Kotian@2005`
- Is admin: `y`

Or run the reset script on production:
```bash
python reset_for_deployment.py
```

## Step 6: Verify Deployment

1. Visit your app: `https://hackotsava-2025.onrender.com`
2. Test login with:
   - Email: `admin@hackotsava.com`
   - Password: `Kotian@2005`
3. Upload some test photos
4. Test face search functionality

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify all environment variables are set
- Ensure requirements.txt is correct

### Database Connection Error
- Verify DATABASE_URL is set
- Check PostgreSQL database is running
- Ensure web service and database are in same region

### Static Files Not Loading
- Check `STATIC_ROOT` in settings.py
- Verify whitenoise middleware is enabled
- Run `python manage.py collectstatic` manually if needed

### Face Recognition Not Working
- Check Cloudinary credentials are correct
- Verify tensorflow/deepface installed correctly
- Check application logs for errors

## 📝 Important Notes

1. **Free Tier Limitations**:
   - Web service sleeps after 15 minutes of inactivity
   - Database limited to 1GB storage
   - 750 hours/month of usage

2. **First Request After Sleep**:
   - May take 30-60 seconds to wake up
   - Subsequent requests will be fast

3. **Monitoring**:
   - Check logs in Render dashboard
   - Set up health checks
   - Monitor database usage

## 🎯 Post-Deployment

1. **Update Domain** (Optional):
   - Add custom domain in Render settings
   - Update `ALLOWED_HOSTS` with your domain

2. **Email Configuration**:
   - Set up SMTP for email notifications
   - Add email environment variables

3. **Backup**:
   - Regularly backup PostgreSQL database
   - Keep local copy of important data

## 🔐 Admin Credentials

**Default Admin Account:**
- Email: `admin@hackotsava.com`
- Password: `Kotian@2005`

⚠️ **IMPORTANT**: Change this password after first login!

## 🎉 Success!

Your Hackotsava 2025 app is now live on Render!

Share the link: `https://your-app-name.onrender.com`

---

**BY PROMOTIONAL TEAM** ✨
