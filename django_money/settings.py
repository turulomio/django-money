## @package settings
##Django settings for dj_books project.
##
##Generated by 'django-admin startproject' using Django 1.11.2.
##
##For more information on this file, see
##https://docs.djangoproject.com/en/1.11/topics/settings/
##
##For the full list of settings and their values, see
##https://docs.djangoproject.com/en/1.11/ref/settings/

import os
from django.urls import reverse_lazy

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

## SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CHANGEME-CHANGEME-CHANGEME-CHANGEME-CHANGEME-CHANGEME'

## @note SECURITY WARNING: don't run with debug turned on in production!
## Defines is a Debug environment
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1' ]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

## Application definitions
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'money',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', #Must be here
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', 
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'money.middleware.MoneyMiddleware', 
]

ROOT_URLCONF = 'django_money.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+"/templates/"],
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


WSGI_APPLICATION = 'django_money.wsgi.application'

## Database connection definitions
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'xulpymoney',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 5432,
    }
}

CONCURRENCY_DB_CONNECTIONS_BY_USER=4

## Locale paths in source distribution
LOCALE_PATHS = (
    BASE_DIR+ '/money/locale/',
)

## Password validation 
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

## Language code
LANGUAGE_CODE = 'en-us'
LANGUAGES=[
    ("en", "English"),  
    ("es",  "Español"), 
    ("fr", "Français") , 
    ("ro", "Romanian"), 
    ("ru", "Russian"), 
]
## Timezone definition
USE_TZ = True
TIME_ZONE = 'UTC'

## Allos internationalization
USE_I18N = True

USE_L10N = True
DATE_FORMAT = "Y-m-d"
DATE_INPUT_FORMATS = ('%Y-%m-%d')

LOGIN_URL = reverse_lazy("login")
LOGIN_REDIRECT_URL = reverse_lazy("home")
LOGOUT_REDIRECT_URL = reverse_lazy("login")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR+ "/money/static/"

## Sets session timeout in seconds.
SESSION_COOKIE_AGE = 3600

## Session cookie age is renewed in every request
SESSION_SAVE_EVERY_REQUEST = True

## Expires session if browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
