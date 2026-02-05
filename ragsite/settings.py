from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'replace-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'ragapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'ragsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ['django.template.context_processors.request']},
    },
]

WSGI_APPLICATION = 'ragsite.wsgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_ROOT = BASE_DIR / 'data' / 'raw'
MEDIA_URL = '/media/'
