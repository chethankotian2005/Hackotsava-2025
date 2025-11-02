# 🎯 Hackotsava 2025 - Event Photo Finder

<div align="center">

![Hackotsava 2025](https://img.shields.io/badge/Hackotsava-2025-8B5CF6?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI-Powered-8B5CF6?style=for-the-badge)

**A national level 30 hours hackathon**

An AI-powered web application that helps event participants find their photos using advanced face recognition technology.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## ✨ Features

### 🔐 Dual User Roles
- **Admin**: Full control over events, photo uploads, and system analytics
- **Regular User**: Browse events, search photos using selfies, and download matches

### 🤖 AI-Powered Face Recognition
- Advanced face detection using DeepFace with ArcFace model (95%+ accuracy)
- **Multi-detector fallback system**: RetinaFace → MTCNN → OpenCV → SSD
- **Adaptive confidence thresholds**: High (95%), Medium (85%), Low (75%)
- **Multiple faces per photo**: Detects and matches ALL people in group photos
- Handles different lighting, angles, and expressions like Google Photos
- L2-normalized embeddings for accurate cosine similarity matching
- Support for multiple faces in photos with separate embeddings

### 📸 Event Management
- Create and manage multiple events
- Bulk photo upload with drag-and-drop support
- Automatic face processing and encoding
- Event privacy controls (public/private)
- Event cover images and metadata

### 🔍 Smart Photo Search
- Upload a selfie to find your photos
- Real-time face matching across event galleries
- Filter results by confidence score
- Batch download matched photos
- View full-size images with lightbox

### 📊 Analytics Dashboard
- Total events, photos, and faces tracked
- Search activity monitoring
- User engagement statistics
- Popular events insights

### 🎨 Modern Dark-Purple Theme
- Cyberpunk/futuristic hackathon aesthetic
- Glassmorphism effects with purple accents
- Fully responsive design
- Smooth animations and transitions
- Custom Orbitron/Audiowide fonts for branding

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL or SQLite (for database)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hackotsava-2025.git
cd hackotsava-2025
```

2. **Create a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

> **Note**: Installing `dlib` and `face_recognition` may require additional system dependencies:
> 
> **Windows**: Install CMake and Visual Studio Build Tools
> ```bash
> pip install cmake
> ```
> 
> **Linux (Ubuntu/Debian)**:
> ```bash
> sudo apt-get update
> sudo apt-get install build-essential cmake
> sudo apt-get install libopenblas-dev liblapack-dev
> sudo apt-get install python3-dev
> ```
> 
> **macOS**:
> ```bash
> brew install cmake
> ```

4. **Set up environment variables**
```bash
# Copy the example env file
copy .env.example .env

# Edit .env and configure your settings
# At minimum, set:
# - SECRET_KEY (generate a strong random key)
# - DEBUG (True for development, False for production)
# - Database credentials (if using PostgreSQL)
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a superuser (Admin)**
```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account with full privileges.

7. **Create static files directory**
```bash
python manage.py collectstatic --noinput
```

8. **Run the development server**
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

---

## 📖 Usage Guide

### For Admins

1. **Login** to your admin account at `/accounts/login/`

2. **Create an Event**
   - Go to Admin Dashboard
   - Click "Create Event"
   - Fill in event details (name, date, location, description)
   - Upload a cover image (optional)
   - Set privacy (public/private)

3. **Upload Photos**
   - Navigate to the event
   - Click "Upload Photos"
   - Select multiple photos (drag & drop supported)
   - Wait for automatic face processing
   - Photos will be available for searching once processed

4. **Monitor Analytics**
   - View dashboard for overall statistics
   - Check recent search activity
   - Monitor popular events
   - Track user engagement

### For Regular Users

1. **Register** an account at `/accounts/register/`

2. **Browse Events**
   - View all public events on the Events page
   - Search for specific events using the search bar

3. **Find Your Photos**
   - Click "Search Photos" on any event
   - Upload a clear selfie (front-facing photo)
   - Adjust matching sensitivity if needed (default: 0.6)
   - Click "Search Photos" and wait for results

4. **Download Photos**
   - View matched photos with confidence scores
   - Click "View" to see full-size image
   - Click "Download" to save individual photos
   - Use "Download All" to batch download all matches

---

## 🏗️ Project Structure

```
hackotsava-2025/
├── hackotsava_project/        # Main project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # URL routing
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config
│
├── accounts/                  # User authentication app
│   ├── models.py              # Custom User model
│   ├── views.py               # Auth views
│   ├── forms.py               # Registration/Login forms
│   └── urls.py                # Auth URLs
│
├── events/                    # Main events app
│   ├── models.py              # Event, Photo, FaceEncoding models
│   ├── views.py               # Event and search views
│   ├── forms.py               # Event and upload forms
│   ├── face_utils.py          # Face recognition utilities
│   ├── admin.py               # Admin interface
│   └── urls.py                # Event URLs
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template with navbar/footer
│   ├── events/                # Event templates
│   │   ├── home.html          # Landing page
│   │   ├── event_list.html    # Events listing
│   │   ├── event_detail.html  # Event details
│   │   ├── gallery.html       # Photo gallery
│   │   ├── search.html        # Face search page
│   │   └── admin/             # Admin templates
│   ├── accounts/              # Auth templates
│   └── errors/                # Error pages (404, 500)
│
├── static/                    # Static files
│   ├── css/
│   │   └── style.css          # Main stylesheet (dark-purple theme)
│   └── js/
│       ├── main.js            # Core JavaScript
│       └── search.js          # Search page functionality
│
├── media/                     # User uploaded files
│   ├── event_photos/          # Event photos
│   ├── event_covers/          # Event cover images
│   └── profile_pics/          # User profile pictures
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── manage.py                  # Django management script
└── README.md                  # This file
```

---

## 🔧 Configuration

### Database Setup

**SQLite (Development - Default)**
```python
# Already configured in settings.py
# No additional setup needed
```

**PostgreSQL (Production - Recommended)**
```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Update .env file:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hackotsava_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Face Recognition Settings

Configure in `.env`:
```bash
# Tolerance: Lower = stricter matching (0.3-0.8)
FACE_RECOGNITION_TOLERANCE=0.6

# Max upload size in bytes (10MB default)
MAX_UPLOAD_SIZE=10485760
```

### Email Configuration (Optional)

For email notifications:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Celery (Optional - For Background Processing)

For asynchronous face processing:
```bash
# Install Redis
pip install redis celery

# Start Redis server
redis-server

# Start Celery worker (in separate terminal)
celery -A hackotsava_project worker -l info
```

---

## 🎨 Design & Branding

### Color Scheme
```css
Primary Purple:    #8B5CF6
Secondary Purple:  #7C3AED
Dark Purple:       #6B21A8
Light Purple:      #C084FC
Accent Purple:     #D8B4FE
Background Black:  #0F0F0F
Card Background:   #1F1F1F
```

### Typography
- **Headers**: Orbitron (or Audiowide as fallback)
- **Body**: Inter
- **Tagline**: "A national level 30 hours hackathon"

### Features
- Dark theme throughout
- Purple gradient accents
- Glassmorphism effects
- Smooth animations
- Responsive design

---

## 🧪 Testing

### Create Test Data

```bash
# Create admin user
python manage.py createsuperuser

# Login and create events through web interface
# Or use Django shell:
python manage.py shell
```

```python
from accounts.models import CustomUser
from events.models import Event
from datetime import date

# Create test admin
admin = CustomUser.objects.create_user(
    username='admin',
    email='admin@hackotsava.com',
    password='admin123',
    role='ADMIN'
)

# Create test event
event = Event.objects.create(
    name='Hackotsava 2025 Kickoff',
    description='The opening ceremony of Hackotsava 2025',
    event_date=date.today(),
    location='Tech Campus, Building A',
    created_by=admin,
    is_public=True
)
```

---

## 🚢 Deployment

### Production Checklist

1. **Update settings for production**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

2. **Use environment variables for secrets**
```bash
# Never commit secrets to Git
# Use .env file with python-decouple
```

3. **Set up static files**
```bash
python manage.py collectstatic
```

4. **Use a production database**
```bash
# PostgreSQL recommended
```

5. **Set up media file storage**
```bash
# Consider AWS S3 or similar for scalability
```

6. **Use Gunicorn/uWSGI**
```bash
pip install gunicorn
gunicorn hackotsava_project.wsgi:application
```

7. **Set up Nginx as reverse proxy**

8. **Enable HTTPS** with Let's Encrypt

9. **Configure CORS and security headers**

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
CMD ["gunicorn", "hackotsava_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 🔐 Security Considerations

- ✅ CSRF protection enabled
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection
- ✅ Secure password hashing
- ✅ File upload validation
- ✅ Rate limiting (recommended for production)
- ✅ HTTPS in production
- ✅ Environment variables for secrets

---

## 🐛 Troubleshooting

### Common Issues

**1. dlib installation fails**
```bash
# Windows: Install Visual Studio Build Tools
# Linux: Install build essentials and cmake
sudo apt-get install build-essential cmake
```

**2. Face detection not working**
```bash
# Check if dlib and face_recognition are properly installed
pip list | grep face-recognition
pip list | grep dlib
```

**3. Images not loading**
```bash
# Check MEDIA_URL and MEDIA_ROOT in settings.py
# Ensure media files are being served in development
```

**4. Static files not loading**
```bash
python manage.py collectstatic
# Check STATIC_URL and STATIC_ROOT settings
```

**5. Database errors**
```bash
# Delete db.sqlite3 and migrations, then:
python manage.py makemigrations
python manage.py migrate
```

---

## 📚 API Documentation

### Face Recognition Utilities

**`detect_faces_in_image(image_path)`**
- Detects faces and returns encodings
- Returns: `[(encoding, location), ...]`

**`compare_faces(known_encodings, face_encoding, tolerance=0.6)`**
- Compares face against known encodings
- Returns: `(matches, distances)`

**`find_matching_photos(selfie_encoding, event)`**
- Finds all photos matching a face in an event
- Returns: `[(photo, confidence), ...]`

**`process_photo_faces(photo_obj)`**
- Processes a photo and stores face encodings
- Returns: `int` (number of faces detected)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Credits

- **Face Recognition**: [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey
- **Web Framework**: [Django](https://www.djangoproject.com/)
- **Fonts**: Orbitron, Audiowide (Google Fonts)
- **Icons**: SVG icons inline

---

## 📧 Support

For support, email hackotsava2025@example.com or open an issue in the repository.

---

## 🎯 Roadmap

- [ ] Mobile app version
- [ ] Email notifications for matches
- [ ] Social media sharing
- [ ] Face clustering for grouping
- [ ] Multi-event search
- [ ] Advanced analytics dashboard
- [ ] API for third-party integrations
- [ ] Batch photo upload improvements
- [ ] Real-time face processing with WebSockets
- [ ] Docker containerization

---

<div align="center">

**Built with ❤️ for Hackotsava 2025**

Made by the Hackotsava Development Team

</div>
