"""
Django settings for meeting service project.
Generated for a microservice architecture with separate auth and meeting services.
"""
import os
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config("DJANGO_SECRET_KEY", default=config("SECRET_KEY"))
DEBUG = config("DJANGO_DEBUG", default=config("DEBUG", default=False, cast=bool), cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS',
                       default=config('ALLOWED_HOSTS',
                                      default='localhost,127.0.0.1,0.0.0.0,auth_service,meeting_service,nginx'),
                       cast=Csv())

# Meeting Service Database Configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("MEETING_POSTGRES_DB"),
        "USER": config("MEETING_POSTGRES_USER"),
        "PASSWORD": config("MEETING_POSTGRES_PASSWORD"),
        "HOST": config("MEETING_POSTGRES_HOST"),
        "PORT": config("MEETING_POSTGRES_PORT"),
    }
}

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "channels",
    "django_redis",
    # Local apps
    "meetings",  # Main meeting app - matches your code structure
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Custom Authentication - Using external auth service
# Since this is a separate service, we'll use a custom authentication backend
AUTHENTICATION_BACKENDS = [
    'meetings.authentication.GoogleOAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# User model - Since you're using separate services, you might need to proxy the User model
# or use the default Django User model with custom authentication
AUTH_USER_MODEL = 'auth.User'  # Using default Django User model

# JWT Configuration for inter-service communication
JWT_SETTINGS = {
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SECRET_KEY': config('JWT_SECRET_KEY'),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Auth service configuration
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_service:8001')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = config("STATIC_ROOT", default=os.path.join(BASE_DIR, "staticfiles"))

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = config("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"))

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "meetings.authentication.GoogleOAuthAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    os.getenv('FRONTEND_URL', 'http://localhost:3000'),
    "http://localhost:80",
    "http://127.0.0.1:80",
]

CORS_ALLOW_CREDENTIALS = True

# Allow both authenticated and anonymous users for meeting joins
ALLOW_ANONYMOUS_MEETING_JOIN = True

# Redis Configuration for WebSocket connections and caching
REDIS_URL = config('REDIS_URL', default='redis://redis:6379/0')

# Channels Configuration for WebSocket support
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# WebRTC Configuration
WEBRTC_SETTINGS = {
    'STUN_SERVERS': config('WEBRTC_STUN_SERVERS', default='stun:stun.l.google.com:19302', cast=Csv()),
    'MEDIA_SERVER_URL': config('MEDIA_SERVER_URL', default='http://localhost:3000'),
    'RECORDING_SERVER_URL': config('RECORDING_SERVER_URL', default='http://localhost:3001'),
}

# Meeting Service Specific Settings
MEETING_SETTINGS = {
    'MAX_PARTICIPANTS_PER_ROOM': 50,
    'DEFAULT_MEETING_DURATION': 60,  # minutes
    'AUTO_RECORDING': False,
    'RECORDING_FORMAT': 'mp4',
    'MAX_RECORDING_SIZE': 1024 * 1024 * 1024,  # 1GB
    'MEETING_CLEANUP_INTERVAL': 24,  # hours
    'MEETING_ID_LENGTH': 9,  # Based on your generate_meeting_id method
    'PASSCODE_LENGTH': 6,    # Based on your generate_passcode method
    'INVITATION_EXPIRY_DAYS': 7,  # Based on your invitation logic
}

# Frontend URL
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Use whitenoise for static files in production
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Session Settings
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'meeting_service.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'meetings': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'channels': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'asgiref': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration for background tasks (optional)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email Configuration (for meeting invitations)
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@prismeet.com")

# Validate email configuration for SMTP backend
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        print("WARNING: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set for SMTP backend")
        print(f"Current EMAIL_HOST_USER: '{EMAIL_HOST_USER}'")
        print("Falling back to console backend for development")
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    else:
        print(f"✓ SMTP Email configured with user: {EMAIL_HOST_USER}")

# Meeting Analytics Settings
ANALYTICS_SETTINGS = {
    'TRACK_BANDWIDTH': True,
    'TRACK_CONNECTION_QUALITY': True,
    'EXPORT_ANALYTICS': True,
    'RETENTION_DAYS': 90,  # How long to keep analytics data
}