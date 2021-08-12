"""
Django settings for fk_management project.

Generated by 'django-admin startproject' using Django 2.2.20.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import environ
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env('env/.env')  # reading .env file


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*",]


# Application definition

INSTALLED_APPS = [
    'dal',  # before django.contrib.admin and grappelli if present:
    'dal_select2',  # before django.contrib.admin and grappelli if present:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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
    'allauth.socialaccount.providers.line',
    # others
    'debug_toolbar',  # debug-toolbar
    'django_extensions',
    "django_bootstrap5",
    "import_export",
    'bootstrap_datepicker_plus',
    "mathfilters",
    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    # "kolo.middleware.KoloMiddleware",
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
    "172.16.0.4", "172.17.0.4", "172.18.0.4",
    "172.19.0.4", "172.20.0.4", "172.21.0.4",
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
    },
    'line': {
        'SCOPE': ['profile', 'openid'],
    },
}
ACCOUNT_EMAIL_VERIFICATION = "none"  # mandatory / optional / none
AUTH_USER_MODEL = "accounts.CustomUser"
SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_FORMS = {
   'signup': 'accounts.forms.UserCreationForm',
}

ENVIRONMENT = "default"

# messages framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format':
                '%(asctime)s [%(levelname)s] [%(process)d-%(thread)d] [%(module)s:%(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        # 'logfile': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'maxBytes': 50000,
        #     'backupCount': 2,
        #     'formatter': 'verbose',
        #     'filename': "/var/log/gunicorn/logfile",
        # },
        # 'elogfile': {
        #     'level': 'ERROR',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'maxBytes': 50000,
        #     'backupCount': 2,
        #     'formatter': 'verbose',
        #     'filename': "/var/log/gunicorn/elogfile",
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

# output email content on console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# LINE
LINE_ACCESS_TOKEN = env('LINE_ACCESS_TOKEN')


# Model Choice: Generator不可
CHOICES_CARD = (
    ("SFC", "SFC"), ("SFC（家族）", "SFC（家族）"), ("GoldPoint", "GoldPoint")
)
CHOICES_KIND_CRON_KAKEIBO = (
    ("monthly", "月次"),
    ("yearly_01", "年次（1月）"), ("yearly_02", "年次（2月）"), ("yearly_03", "年次（3月）"),
    ("yearly_04", "年次（4月）"), ("yearly_05", "年次（5月）"), ("yearly_06", "年次（6月）"),
    ("yearly_07", "年次（7月）"), ("yearly_08", "年次（8月）"), ("yearly_09", "年次（9月）"),
    ("yearly_10", "年次（10月）"), ("yearly_11", "年次（11月）"), ("yearly_12", "年次（12月）"),
)
CHOICES_KIND_TARGET = (
    ("総資産", "総資産"),
)
CHOICES_WAY = (
    ("振替", "振替"), ("支出（現金）", "支出（現金）"), ("支出（カード）", "支出（カード）"), ("収入", "収入"),
    ("その他", "その他"),
)
CHOICES_CURRENCY = (
    ("JPY", "JPY"), ("USD", "USD"),
)
CHOICES_EXCHANGE_METHOD = (
    ("Wire", "Wire"), ("prestia", "prestia")
)

# MAPPING
MAPPING_RESOURCE = {
    "SBI敬士": "SBI",
    "投資口座": "投資元本",
    "一般財形": "財形",
}
MAPPING_WAY = {
    "支出（現金）": "支出（現金）",
    "支出（クレジット）": "支出（カード）",
    "支出（Suica）": "その他",
    "引き落とし": "支出（現金）",
    "収入": "収入",
    "振替": "振替",
    "共通支出": "その他",
    "その他": "その他",
}