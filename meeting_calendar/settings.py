from pathlib import Path
from typing import Union
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # deps
    'timezone_field',
    'django_utz',
    'rest_framework_api_key',

    # apps
    'users.apps.UsersConfig',
    'dashboard.apps.DashboardConfig',
    'booking.apps.BookingConfig',
    'news.apps.NewsConfig',
    'links.apps.LinksConfig',
    'tokens.apps.TokensConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_utz.middleware.DjangoUTZMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meeting_calendar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "meeting_calendar/templates")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meeting_calendar.wsgi.application'


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
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.UserAccount'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "meeting_calendar/static")
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SITE_NAME = os.getenv("SITE_NAME", "Meeting Calendar")

SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")


LOGIN_URL = 'users:signin'

LOGIN_REDIRECT_URL = 'dashboard:dashboard'


# EMAIL SETTINGS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv("EMAIL_HOST")

EMAIL_PORT = os.getenv("EMAIL_PORT")

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() == "true"

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


# A list of models that should only be accessible by admin users
ADMIN_ONLY_MODELS = [
    "booking.models.UnavailablePeriod",
    "links.models.Link",
]

def _parse_validity_period(period: Union[str, int]) -> int:
    """
    Converts a password reset token validity period in hours to a valid value.

    If the value set is not valid, a default of 24.
    """
    try:
        return int(period)
    except (ValueError, TypeError):
        return 24

PASSWORD_RESET_TOKEN_VALIDITY_PERIOD = _parse_validity_period(os.getenv("PASSWORD_RESET_TOKEN_VALIDITY_PERIOD"))


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


if DEBUG is False:
    ALLOWED_HOSTS = ["*"] # Set to your domain

else:
    ALLOWED_HOSTS = ["*"]
