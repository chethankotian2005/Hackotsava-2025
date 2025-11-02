"""
One-time admin initialization view
Visit /init-admin-secret-setup/ to create the admin user
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def init_admin(request):
    """Create admin user if it doesn't exist"""
    User = get_user_model()
    email = 'admin@hackotsava.com'
    password = 'Kotian@2005'
    
    if User.objects.filter(email=email).exists():
        return HttpResponse('⚠️ Admin user already exists!<br><a href="/admin/">Go to Admin Panel</a>', status=200)
    
    try:
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='Hackotsava'
        )
        return HttpResponse(
            f'✅ Admin user created successfully!<br><br>'
            f'<strong>Email:</strong> {email}<br>'
            f'<strong>Password:</strong> {password}<br><br>'
            f'<a href="/admin/">Go to Admin Panel</a>',
            status=201
        )
    except Exception as e:
        return HttpResponse(f'❌ Error creating admin: {e}', status=500)
