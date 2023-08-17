import environ
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()


env = environ.Env()
environ.Env.read_env()
# ...
# # Your secret key
SECRET_KEY = os.environ.get("SECRET_KEY")


from pathlib import Path

# # # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!


# Application definition

INSTALLED_APPS = [
    "app",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "phonenumber_field",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
        "DIRS": [],
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


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# =================local database======================

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "HOST": os.getenv("DB_HOST"),
#     }
# }

# =========heroku database==================
DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "app/static/"
# MEDIA_URL = "images/"
# STATICFILES_DIRS = [os.path.join(BASE_DIR / "static")]
# MEDIA_ROOT = os.path.join(BASE_DIR, "app/static/")


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_DIRS = [BASE_DIR / "static", "media"]
MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

# Add your email host, port, username, and password here if you're using a SMTP backend for sending emails.
# For example, if you're using Gmail SMTP to send emails, you'd configure it like this:

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "bryanmcmurry7@gmail.com"
EMAIL_HOST_PASSWORD = "urbedxlmfsslymho"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ALLOWED_HOSTS = [
    "wilco-app-c6223eb282aa.herokuapp.com",
    "127.0.0.1",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://wilco-app-c6223eb282aa.herokuapp.com",
    "https://buy.stripe.com/test_28o2aAafGeRCcPC5kk",
]

PRODUCT_PRICE = "price_1NdxTFCffthPIRLKUftoF4Wz"

# settings.py

# # Set the value for SECURE_HSTS_SECONDS (HTTP Strict Transport Security)
# SECURE_HSTS_SECONDS = 31536000  # One year in seconds

# # Enable secure SSL redirect
# SECURE_SSL_REDIRECT = True

# # Set a strong and random SECRET_KEY
# SECRET_KEY = "your-long-random-secret-key"

# # Ensure secure session cookies
# SESSION_COOKIE_SECURE = True

# # Ensure secure CSRF cookies
# CSRF_COOKIE_SECURE = True

# # Set DEBUG to False in production
DEBUG = True
REDIRECT_DOMAIN = "https://wilco-app-c6223eb282aa.herokuapp.com/"
STRIPE_PUBLIC_KEY = "pk_test_51NbRsdCffthPIRLKv0yaJi2mlLwitUqqcipZYX3mdsreLqTrHy0SmO7scfqmercaOfWZQcLObh7uzKyUjUFsVj3r00mBVR5D9z"
STRIPE_SECRET_KEY = "sk_test_51NbRsdCffthPIRLKsKEjqXGQo3H7zcpoulRxnXo0Wrj46cpkhVmysuZ4lmhDDOc0dd7Uk1mfolG1HIYHqFjoVWbw00jj6IpQCL"
STRIPE_WEBHOOK_SECRET = "whsec_DeI7ADiOqIcDdWHLhGlETJP0audtpDCH"
