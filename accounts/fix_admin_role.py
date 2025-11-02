"""
Fix existing admin user role
Visit /fix-admin-role/ to set the admin role correctly
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def fix_admin_role(request):
    """Fix the role for existing admin user"""
    User = get_user_model()
    
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        return HttpResponse(
            f'✅ Admin role fixed successfully!<br><br>'
            f'<strong>Username:</strong> {admin_user.username}<br>'
            f'<strong>Email:</strong> {admin_user.email}<br>'
            f'<strong>Role:</strong> {admin_user.role}<br>'
            f'<strong>Is Staff:</strong> {admin_user.is_staff}<br>'
            f'<strong>Is Superuser:</strong> {admin_user.is_superuser}<br><br>'
            f'<a href="/admin/">Go to Admin Panel</a><br>'
            f'<small>Please log out and log back in for changes to take effect.</small>',
            status=200
        )
    except User.DoesNotExist:
        return HttpResponse('❌ Admin user not found!', status=404)
    except Exception as e:
        return HttpResponse(f'❌ Error fixing admin role: {e}', status=500)
