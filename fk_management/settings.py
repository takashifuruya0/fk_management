"""
Django settings for fk_management project.

Generated by 'django-admin startproject' using Django 2.2.20.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env('.env')  # reading .env file


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h)kw2#3knd9ft)2q(9w@n(imv(gox4$hz&la^)1qntq@)!ze01'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*",]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # app
    "accounts",
    "kakeibo",
    "asset",
    "work",
    # allauth
    'allauth',
    'django.contrib.sites',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # others
    'debug_toolbar',  # debug-toolbar
    'django_extensions',
    "django_bootstrap5",
    "import_export",
    # 'fontawesome-free',
    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    "kolo.middleware.KoloMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # debug-toolbar
    'django_currentuser.middleware.ThreadLocalUserMiddleware',  # get_current_authenticated_user
]

ROOT_URLCONF = 'fk_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "fk_management/templates",
            os.path.join(BASE_DIR, 'fk_management', 'templates', 'allauth')
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

WSGI_APPLICATION = 'fk_management.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# staticファイルのURL
STATIC_URL = '/static/'
# project全体のstaticファイル格納場所
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "staticfiles"),
)
# collectstatic の格納場所
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# debug-toolbar
INTERNAL_IPS = [
    '0.0.0.0', '127.0.0.1',
    "172.22.0.4", "172.23.0.4", "172.24.0.4",
    "172.25.0.4", "172.26.0.4", "172.27.0.4",
    "172.28.0.4", "172.29.0.4", "172.27.30.4",
    "172.31.0.4",
]

# allauth
SITE_ID = 1
LOGIN_URL = "/auth/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = True
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    "allauth.account.auth_backends.AuthenticationBackend",
)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        "SCOPE": [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
ACCOUNT_EMAIL_VERIFICATION = "none"  # mandatory / optional / none
AUTH_USER_MODEL = "accounts.CustomUser"
SOCIALACCOUNT_AUTO_SIGNUP = False
#ACCOUNT_FORMS = {
#    'signup': 'accounts.forms.CustomSignupForm',
#}
