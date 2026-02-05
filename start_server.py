#!/usr/bin/env python
"""
Simple Django WSGI server
"""
import os
import sys
import warnings
import wsgiref.simple_server

# Suppress numpy warnings
warnings.filterwarnings('ignore')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ragsite.settings")

# Setup Django
import django
django.setup()

from ragsite.wsgi import application

print("\n" + "="*60)
print("CONTRACT RAG SERVER")
print("="*60)
print("\n✓ Starting server on http://127.0.0.1:8000")
print("  Open browser and go to: http://127.0.0.1:8000/")
print("\n  (Press Ctrl+C to stop)\n")
print("="*60 + "\n")

# Create server
httpd = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
print("Server is ready. Waiting for requests...\n")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n\nShutting down...")
    sys.exit(0)
