"""
Check admin user status in database
Visit /check-admin-status/ to see admin user details
"""
from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate

def check_admin_status(request):
    """Check if admin user exists and can authenticate"""
    User = get_user_model()
    
    output = "<h1>Admin User Diagnostic Report</h1><hr>"
    
    # Check if admin user exists
    try:
        admin_user = User.objects.get(username='admin')
        output += "<h2>✅ Admin User Found</h2>"
        output += f"<strong>Username:</strong> {admin_user.username}<br>"
        output += f"<strong>Email:</strong> {admin_user.email}<br>"
        output += f"<strong>Role:</strong> {admin_user.role}<br>"
        output += f"<strong>Is Active:</strong> {admin_user.is_active}<br>"
        output += f"<strong>Is Staff:</strong> {admin_user.is_staff}<br>"
        output += f"<strong>Is Superuser:</strong> {admin_user.is_superuser}<br>"
        output += f"<strong>Date Joined:</strong> {admin_user.date_joined}<br>"
        output += f"<strong>Last Login:</strong> {admin_user.last_login}<br>"
        output += f"<strong>Has Usable Password:</strong> {admin_user.has_usable_password()}<br>"
        
        # Try to authenticate
        output += "<hr><h2>Authentication Test</h2>"
        auth_user = authenticate(username='admin', password='Kotian@2005')
        if auth_user:
            output += "✅ <strong>Authentication successful!</strong> Password is correct.<br>"
        else:
            output += "❌ <strong>Authentication failed!</strong> Password might be incorrect.<br>"
            output += "<p>Possible issues:</p><ul>"
            output += "<li>Password was changed</li>"
            output += "<li>User is not active</li>"
            output += "<li>Password hash is corrupted</li>"
            output += "</ul>"
            
    except User.DoesNotExist:
        output += "<h2>❌ Admin User NOT Found</h2>"
        output += "<p>No user with username 'admin' exists in the database.</p>"
        output += f'<p><a href="/fix-admin-role/">Click here to create admin user</a></p>'
    
    # List all users
    output += "<hr><h2>All Users in Database</h2>"
    all_users = User.objects.all()
    if all_users.exists():
        output += f"<p>Total users: {all_users.count()}</p><ul>"
        for user in all_users:
            output += f"<li>{user.username} - Role: {user.role} - Staff: {user.is_staff} - Superuser: {user.is_superuser}</li>"
        output += "</ul>"
    else:
        output += "<p>No users found in database.</p>"
    
    output += '<hr><p><a href="/fix-admin-role/">Reset Admin User</a> | <a href="/admin/">Go to Admin Panel</a></p>'
    
    return HttpResponse(output)
