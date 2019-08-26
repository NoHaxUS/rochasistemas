import os
#import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't9xein@q$yf$w+ks2m&hr&53j1n@rtyg7o(b1(-)ffz7nce-kg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEV_MODE = False
DB_SWAP_LOCAL = False

ALLOWED_HOSTS = ['*']

APP_VERBOSE_NAME = 'sitename'

# Application definition

INSTALLED_APPS = [
    'config.apps.MyAdminConfig',    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'corsheaders',    
    'rest_framework',
    'filters',
    'core',
    'user',
    'history',
    'utils',
    'ticket',
    'cashier',
    'updater'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.ReadKeyMiddleware'
]

AUTH_USER_MODEL = 'user.CustomUser'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]


CACHES = {
    'local_dev': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'KEY_PREFIX': 'sitename'
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}


WSGI_APPLICATION = 'config.wsgi.application'


# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if DB_SWAP_LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'bet_bola_api',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
            'CHARSET':'UTF8'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'bet_bola_api',
            'USER': 'bet_bola_user',
            'PASSWORD': 'r7fcfEGEQEzGLN6y',
            'HOST': 'localhost',
            'PORT': '5432',
            'CHARSET':'UTF8'
        }
    }


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://806cfdecfa1e4918a4e18fc53d98f10c@sentry.io/1497286",
    integrations=[DjangoIntegration()]
)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

from django.utils.translation import gettext_lazy as _

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

LANGUAGES = (
    ('en', _('Inglês')),
    ('pt-br', _('Português'))
)

LANGUAGE_CODE = 'pt-br'

#Decimal
DECIMAL_SEPARATOR = '.'
#USE_THOUSAND_SEPARATOR = True

#Encoding
DEFAULT_CHARSET = 'utf-8'

#Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'betemailsender@gmail.com'
EMAIL_HOST_PASSWORD = 'plataformabet'
EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'Pablo <noreply@example.com>'

#Zones
TIME_ZONE = 'UTC'
TIME_ZONE_LOCAL = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = False


#Statis Files
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'


REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%d %B %Y %H:%M",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    )
}

def jwt_response_payload_handler(token, user=None, request=None):    
    if user.is_active and int(request.POST.get('store')) == user.my_store.pk:
        return {
            'token': token,
            'user': {
                'pk': user.pk,
                'user': user.username,
                'user_type': user.user_type,
                'name' : user.first_name
            }
        }
    else:
        return {
            'token': None
        }

import datetime

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': jwt_response_payload_handler,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=259200)
}

JWT_AUTH_COOKIE ='token'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 259200

CORS_ORIGIN_ALLOW_ALL = True

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    'SecurityAuthorization',
]