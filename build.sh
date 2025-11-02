#!/usr/bin/env bash
# Build script for Render

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create initial admin user using Python directly
echo "Creating admin user..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hackotsava_project.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = 'admin@hackotsava.com'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password='Kotian@2005', first_name='Admin', last_name='Hackotsava')
    print('✅ Admin user created: admin@hackotsava.com / Kotian@2005')
else:
    print('ℹ️  Admin user already exists')
"
echo "Admin user setup complete!"
