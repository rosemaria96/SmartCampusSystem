import os
import sys
import django
import shutil

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Delete all migration files except __init__.py
apps = ['users', 'academics', 'finance', 'communication', 'assessments']
for app in apps:
    migrations_dir = os.path.join(app, 'migrations')
    if os.path.exists(migrations_dir):
        for file in os.listdir(migrations_dir):
            if file != '__init__.py' and file != '__pycache__':
                file_path = os.path.join(migrations_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory {file_path}")

print("\nAll old migrations deleted!")

# Setup Django
django.setup()

# Now run makemigrations
from django.core.management import call_command

print("\nCreating fresh migrations...")
try:
    call_command('makemigrations')
    print("\nMigrations created successfully!")
    
    print("\nApplying migrations...")
    call_command('migrate')
    print("\nMigrations applied successfully!")
    
    print("\nCreating superuser...")
    from users.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@smartcampus.com',
            password='admin123',
            name='System Administrator',
            role='ADMIN'
        )
        print("Superuser 'admin' created with password 'admin123'")
    else:
        print("Superuser already exists")
        
    print("\n✅ Database setup complete!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
