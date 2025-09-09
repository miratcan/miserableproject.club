import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment
env = environ.Env(
    DJANGO_DEBUG=(bool, True),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='dev-insecure-key-change-me')
DEBUG = env('DJANGO_DEBUG')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    # Third-party
    'taggit',

    # Local apps
    'apps.core',
    'apps.submissions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
SITE_ID = int(env('SITE_ID', default='1'))

# Admin URL
ADMIN_URL = env('ADMIN_URL', default='admin/')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Security defaults for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# SEO defaults
SITE_NAME = env('SITE_NAME', default='miserableprojects.directory')
DEFAULT_OG_IMAGE = env('MISERABLEPROJECT_DEFAULT_OG_IMAGE', default=env('DEFAULT_OG_IMAGE', default='/static/img/og-placeholder.svg'))

# Email/Anymail configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='no-reply@miserableprojects.directory')
USE_ANYMAIL = env.bool('USE_ANYMAIL', default=False)
ANYMAIL_BACKEND = env('ANYMAIL_BACKEND', default=None)  # e.g. 'anymail.backends.mailgun.EmailBackend'
if USE_ANYMAIL and ANYMAIL_BACKEND:
    INSTALLED_APPS.append('anymail')
    EMAIL_BACKEND = ANYMAIL_BACKEND
    # Common ANYMAIL dict; set provider-specific keys via env
    ANYMAIL = {
        'MAILGUN_API_KEY': env('MAILGUN_API_KEY', default=''),
        'MAILGUN_SENDER_DOMAIN': env('MAILGUN_DOMAIN', default=''),
    }

# Fail fast if production missing a real secret key
if not DEBUG and SECRET_KEY == 'dev-insecure-key-change-me':
    raise RuntimeError('DJANGO_SECRET_KEY must be set in production')
