#!/usr/bin/env python
import os
import sys
import warnings

# Suppress numpy
warnings.filterwarnings('ignore', category=RuntimeWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ragsite.settings')

print("="*60)
print("DJANGO STARTUP DIAGNOSTIC")
print("="*60)

try:
    print("\n1. Importing django...")
    import django
    print(f"   ✓ Django {django.VERSION} imported")
    
    print("\n2. Setting up Django...")
    django.setup()
    print("   ✓ Django setup complete")
    
    print("\n3. Importing models...")
    from django.apps import apps
    print(f"   ✓ Loaded {len(list(apps.get_app_configs()))} apps")
    
    print("\n4. Checking templates...")
    from django.template import engines
    print(f"   ✓ Template engines ready")
    
    print("\n5. Checking static files...")
    from django.contrib.staticfiles.storage import StaticFilesStorage
    print("   ✓ Static files storage ready")
    
    print("\n6. Running system checks...")
    from django.core.management import execute_from_command_line
    sys.argv = ['manage.py', 'check', '--verbosity=2']
    try:
        execute_from_command_line(sys.argv)
    except SystemExit as e:
        if e.code == 0:
            print("   ✓ All checks passed!")
        else:
            print(f"   ✗ System exit with code {e.code}")
            raise
    
    print("\n7. Server ready!")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ ERROR at step: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
