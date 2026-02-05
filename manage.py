#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ragsite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise ImportError('Django is required to run this project. Install it in your virtualenv.')
    execute_from_command_line(sys.argv)
