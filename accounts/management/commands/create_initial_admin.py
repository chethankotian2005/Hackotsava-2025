"""
Management command to create initial admin user if it doesn't exist
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates initial admin user if no admin exists'

    def handle(self, *args, **options):
        admin_email = 'admin@hackotsava.com'
        
        # Check if admin already exists
        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user {admin_email} already exists'))
            return
        
        # Create admin user
        try:
            User.objects.create_superuser(
                email=admin_email,
                password='Kotian@2005',
                first_name='Admin',
                last_name='Hackotsava'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully created admin user: {admin_email}'))
            self.stdout.write(self.style.SUCCESS(f'   Password: Kotian@2005'))
            self.stdout.write(self.style.WARNING('   ⚠️  REMEMBER TO CHANGE PASSWORD AFTER FIRST LOGIN!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating admin user: {e}'))
