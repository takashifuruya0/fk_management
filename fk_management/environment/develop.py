from fk_management.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        "USER": env('DB_USER'),
        "PASSWORD": env('DB_PASSWORD'),
        'HOST': env("DB_HOST"),
        "PORT": env('DB_PORT'),
        "ATOMIC_REQUESTS": True,
    }
}

ENVIRONMENT = "develop"

# sendgrid by django-sendgrid-v5==1.1.0
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY", None)
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
DEFAULT_FROM_EMAIL = "noreply@fk-management.com"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = "true"