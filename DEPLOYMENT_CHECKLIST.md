# ✅ Deployment Checklist

## Pre-Deployment Tasks

### 1. Database Reset
- [x] Run `python reset_for_deployment.py`
- [x] All photos deleted from database
- [x] All events deleted
- [x] All search history cleared
- [x] Admin password set to `Kotian@2005`

### 2. Cloudinary Cleanup
- [ ] Go to https://cloudinary.com/console
- [ ] Delete all uploaded photos from Media Library
- [ ] Verify storage is cleared

### 3. Environment Configuration
- [ ] `.env` file created with production values
- [ ] `SECRET_KEY` generated (use Django's get_random_secret_key)
- [ ] `DEBUG` set to `False`
- [ ] Cloudinary credentials added
- [ ] `ALLOWED_HOSTS` includes `.onrender.com`

### 4. Code Cleanup
- [x] Updated `.gitignore` to exclude test files
- [x] requirements.txt updated with production packages
- [x] Procfile created for Render
- [x] build.sh created for Render
- [x] runtime.txt specifies Python 3.11.0
- [x] Settings.py updated for production

### 5. Git Repository
- [ ] Initialize git: `git init`
- [ ] Add all files: `git add .`
- [ ] Commit: `git commit -m "Initial commit - Ready for deployment"`
- [ ] Create GitHub repository
- [ ] Push to GitHub: `git push -u origin main`

## Render Deployment

### 6. Create Web Service
- [ ] Go to https://dashboard.render.com/
- [ ] Click "New" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Configure service:
  - Name: `hackotsava-2025`
  - Build Command: `./build.sh`
  - Start Command: `gunicorn hackotsava_project.wsgi:application`
  - Instance Type: Free

### 7. Add Environment Variables
- [ ] `SECRET_KEY` (generate new)
- [ ] `DEBUG=False`
- [ ] `CLOUDINARY_CLOUD_NAME`
- [ ] `CLOUDINARY_API_KEY`
- [ ] `CLOUDINARY_API_SECRET`
- [ ] `ALLOWED_HOSTS=.onrender.com`
- [ ] `PYTHON_VERSION=3.11.0`

### 8. Create PostgreSQL Database
- [ ] Create new PostgreSQL database
- [ ] Link to web service (DATABASE_URL auto-added)

### 9. Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Check logs for errors

## Post-Deployment

### 10. Verify Deployment
- [ ] Visit app URL
- [ ] Login with admin@hackotsava.com / Kotian@2005
- [ ] Create test event
- [ ] Upload test photos
- [ ] Test face search
- [ ] Test download functionality
- [ ] Test on mobile device

### 11. Security
- [ ] Change admin password after first login
- [ ] Verify DEBUG is False
- [ ] Check HTTPS is working
- [ ] Test CSRF protection

### 12. Documentation
- [ ] Share app URL with team
- [ ] Document any custom configurations
- [ ] Note any issues or workarounds

## 🎉 Deployment Complete!

Your app should be live at: `https://your-app-name.onrender.com`

### Important Notes:
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Database limited to 1GB on free tier
- Monitor logs regularly for issues

---

**BY PROMOTIONAL TEAM** ✨
