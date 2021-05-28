from fk_management.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        "USER": env('DB_USER'),
        "PASSWORD": env('DB_PASSWORD'),
        'HOST': env("DB_HOST"),
        "POST": env('DB_PORT'),
        "ATOMIC_REQUESTS": True,
    }
}