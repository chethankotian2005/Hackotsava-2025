"""
Fix existing admin user role
Visit /fix-admin-role/ to set the admin role correctly
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def fix_admin_role(request):
    """Create or fix admin user with proper role"""
    User = get_user_model()
    
    try:
        # Try to get existing admin user
        admin_user = User.objects.get(username='admin')
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        action = "Fixed"
        
    except User.DoesNotExist:
        # Create new admin user if doesn't exist
        try:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@hackotsava.com',
                password='Kotian@2005',
                role='ADMIN'
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            action = "Created"
        except Exception as create_error:
            return HttpResponse(f'❌ Error creating admin user: {create_error}', status=500)
    
    return HttpResponse(
        f'✅ Admin user {action.lower()} successfully!<br><br>'
        f'<strong>Username:</strong> {admin_user.username}<br>'
        f'<strong>Email:</strong> {admin_user.email}<br>'
        f'<strong>Password:</strong> Kotian@2005<br>'
        f'<strong>Role:</strong> {admin_user.role}<br>'
        f'<strong>Is Staff:</strong> {admin_user.is_staff}<br>'
        f'<strong>Is Superuser:</strong> {admin_user.is_superuser}<br><br>'
        f'<a href="/admin/">Go to Admin Panel</a><br>'
        f'<small>Log in with username "admin" and password "Kotian@2005"</small>',
        status=200
    )
