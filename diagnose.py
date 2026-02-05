import django
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ragsite.settings')

try:
    print("Django version:", django.VERSION)
    print("Python version:", sys.version)
    print("Setting up Django...")
    django.setup()
    print("Django setup complete!")
    
    print("\nRunning system checks...")
    from django.core.management import call_command
    call_command('check', verbosity=2)
    print("System check passed!")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
