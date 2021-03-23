from .settings import BASE_DIR
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rtauz!ez&*um9hd8^@h-iz(_$r6+ktr(o8!#qxd+wk=d2nskix'

# Provider specific settings
# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '67240427755-6kobovjsqao11iqbtmr8ca0f4nghm98o.apps.googleusercontent.com',
            'secret': 'Kh4LcqcxLxM9uRXRVXIfqJKi',
            'key': ''
        }
    }
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


