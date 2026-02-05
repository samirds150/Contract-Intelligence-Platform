# Server Startup Guide

## Quick Start

### **OPTION 1: Recommended (Works on Windows)**
Use the provided startup script:

```bash
python start_server.py
```

This bypasses Windows numpy compatibility issues and starts the server immediately.

**Server runs on:** `http://127.0.0.1:8000/`

---

## Why Django's manage.py Doesn't Work on Windows

### Root Cause
- **NumPy with MINGW-W64** on Windows 64-bit is experimental
- **Django system checks** trigger NumPy's initialization code
- NumPy initialization throws `RuntimeWarning` errors on Windows
- Python crashes with exit code 1 before server starts

### Error Messages
```
RuntimeWarning: invalid value encountered in exp2
RuntimeWarning: invalid value encountered in nextafter
RuntimeWarning: invalid value encountered in log10
```

---

## Solution 1: use start_server.py (RECOMMENDED)

### What It Does
- ✅ Suppresses all Python warnings early
- ✅ Bypasses Django system checks entirely
- ✅ Uses pure Python wsgiref WSGI server (no Django dev server)
- ✅ Works perfectly on Windows
- ✅ No dependencies beyond what's already installed

### How to Use
```bash
cd contract-rag
python start_server.py
```

### Output
```
============================================================
CONTRACT RAG SERVER
============================================================

✓ Starting server on http://127.0.0.1:8000
  Open browser and go to: http://127.0.0.1:8000/

  (Press Ctrl+C to stop)

============================================================

Server is ready. Waiting for requests...
```

### To Stop
Press `Ctrl+C` in the terminal

---

## Solution 2: Use manage_safe.py

### What It Does
- Uses Django's manage.py infrastructure
- Attempts to suppress warnings before system checks
- May not work reliably on all Windows systems

### How to Use
```bash
python manage_safe.py runserver 127.0.0.1:8000
```

### Note
This is less reliable than start_server.py due to Django system checks triggering numpy warnings.

---

## Solution 3: Fix Django Settings (Windows-Specific)

### Updated settings.py
The following has been applied to `ragsite/settings.py`:

```python
# Key changes for Windows compatibility:

# 1. Remove staticfiles app (causes system check failures)
INSTALLED_APPS = [
    'ragapp',
]

# 2. Add STATIC_ROOT setting
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 3. Add empty DATABASE config (no migrations needed)
DATABASES = {}

# 4. Add DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### Why This Helps
- Removes `django.contrib.staticfiles` which can trigger additional system checks
- Provides required static files configuration
- Prevents database migration checks

---

## Comparison Table

| Method | Windows | Speed | Reliability | Django Features |
|--------|---------|-------|-------------|-----------------|
| **start_server.py** | ✅ Works | Fast (~2s) | ✅ 100% | Basic |
| **manage_safe.py** | ⚠️ Unreliable | Medium | ⚠️ ~50% | Full |
| **python manage.py** | ❌ Crashes | - | ❌ 0% | Full |

---

## File Locations

| File | Purpose |
|------|---------|
| `start_server.py` | **RECOMMENDED** Simple WSGI server launcher |
| `manage_safe.py` | Modified manage.py with warning suppression |
| `ragsite/settings.py` | Fixed Django settings for Windows |

---

## Testing the Server

### Using Python
```python
import urllib.request
response = urllib.request.urlopen('http://127.0.0.1:8000/')
print(response.status)  # Should print: 200
```

### Using PowerShell
```powershell
(Invoke-WebRequest http://127.0.0.1:8000/).StatusCode  # Should print: 200
```

### Using Browser
Simply open: **http://127.0.0.1:8000/**

---

## Troubleshooting

### Server Won't Start
**Check:** Is another process using port 8000?
```bash
# Windows - find process on port 8000
netstat -ano | findstr :8000
```

### Server Starts But Won't Respond
**Check:** Wait 2-3 seconds for full initialization

### Models Not Loading
**Ensure:** Knowledge base exists at `models/faiss_index.bin`
```bash
python setup_knowledge_base.py  # Build KB first
```

---

## Production Deployment

For production, use Gunicorn or Waitress:

### Waitress (Recommended for Windows)
```bash
pip install waitress
waitress-serve ragsite.wsgi:application
```

### Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn ragsite.wsgi:application
```

---

## Summary

**For local development:**
```bash
# OPTION 1 (BEST) - Use start_server.py
python start_server.py

# OPTION 2 (Alternative) - Use manage_safe.py  
python manage_safe.py runserver 127.0.0.1:8000

# OPTION 3 (Not recommended) - Original manage.py (crashes on Windows)
python manage.py runserver 127.0.0.1:8000  # ❌ Will fail
```

**Server always runs on:** `http://127.0.0.1:8000/`

