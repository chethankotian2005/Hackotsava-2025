"""
Quick fix to ensure admin user exists and has correct permissions
Visit /quick-fix-admin/ to fix the admin user
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def quick_fix_admin(request):
    """Ensure admin user exists with all correct settings"""
    User = get_user_model()
    
    output = "<h1>🔧 Admin User Quick Fix</h1><hr>"
    
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hackotsava.com',
                'is_staff': True,
                'is_superuser': True,
                'role': 'ADMIN'
            }
        )
        
        # Update fields regardless
        admin_user.email = 'admin@hackotsava.com'
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        
        # Set password
        admin_user.set_password('Kotian@2005')
        admin_user.save()
        
        action = "Created" if created else "Updated"
        
        output += f"<h2>✅ Admin User {action}!</h2>"
        output += f"<p><strong>Username:</strong> {admin_user.username}</p>"
        output += f"<p><strong>Email:</strong> {admin_user.email}</p>"
        output += f"<p><strong>Password:</strong> Kotian@2005</p>"
        output += f"<p><strong>Role:</strong> {admin_user.role}</p>"
        output += f"<p><strong>Is Admin:</strong> {admin_user.is_admin()}</p>"
        output += f"<p><strong>Is Active:</strong> {admin_user.is_active}</p>"
        output += f"<p><strong>Is Staff:</strong> {admin_user.is_staff}</p>"
        output += f"<p><strong>Is Superuser:</strong> {admin_user.is_superuser}</p>"
        
        output += "<hr>"
        output += "<h3>✅ All permissions verified!</h3>"
        output += "<p>You can now log in to the admin panel.</p>"
        output += '<p><a href="/admin/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Admin Panel</a></p>'
        
        return HttpResponse(output)
        
    except Exception as e:
        output += f"<h2>❌ Error</h2>"
        output += f"<p>{str(e)}</p>"
        return HttpResponse(output, status=500)
