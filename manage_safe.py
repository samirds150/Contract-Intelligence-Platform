#!/usr/bin/env python
"""
Custom manage.py that works on Windows with numpy/MINGW issues
"""
import sys
import os
import warnings
import django
from django.conf import settings

# Suppress warnings IMMEDIATELY
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ragsite.settings")

# Monkey patch Django to skip system checks
from django.core import management
original_check = management.call_command

def patched_call_command(name, *args, **options):
    # Skip system checks for runserver
    if name == 'runserver':
        options['skip_checks'] = True
    return original_check(name, *args, **options)

management.call_command = patched_call_command

# Now run the command
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
