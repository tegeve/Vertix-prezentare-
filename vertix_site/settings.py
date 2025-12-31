
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l1jfr9e%zkb6x^5e(5nrd1a=m5_d9kzb@clg-l(w_&_ldf&z&s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "website",
    "accounts",
    "portal",
    "jazzmin",
    "analytics",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "portal.middleware.BlockBlockedIPMiddleware",
    "analytics.middleware.PageViewMiddleware",
]

ROOT_URLCONF = 'vertix_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "website.context_processors.site_settings",

            ],
        },
    },
]

WSGI_APPLICATION = 'vertix_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/



TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = "ro"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("ro", "Română"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "staticfiles"
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB

DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE  # protejează request body
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE  # fișiere > prag merg în temp
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = 'home'
TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "website.context_processors.popup_messages",
]

INSTALLED_APPS += ["tinymce"]

TINYMCE_DEFAULT_CONFIG = {
    "height": 560,
    "width": "100%",
    "menubar": True,
    "plugins": "image link media table code lists autoresize",
    "toolbar": "undo redo | styles | bold italic underline | bullist numlist | link image media | table | code",
}

INSTALLED_APPS += [
    "django_recaptcha",
]

# reCAPTCHA v3
RECAPTCHA_PUBLIC_KEY = "SITE_KEY"
RECAPTCHA_PRIVATE_KEY = "SECRET_KEY"
RECAPTCHA_REQUIRED_SCORE = 0.5  # ajustezi 0.3-0.7
RECAPTCHA_DOMAIN = "www.google.com"

# recomandat în prod:
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "vertix-cache",
    }
}

JAZZMIN_SETTINGS = {
    "site_title": "Vertix Admin",
    "site_header": "Vertix",
    "site_brand": "Vertix",
    "welcome_sign": "Bun venit în administrare",
    "copyright": "Vertix",
    "search_model": ["website.ContactMessage", "website.BlogPost", "website.Service"],

    "topmenu_links": [
        {"name": "Vizualizare site", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"name": "Analytics", "url": "/ro/admin/analytics/", "new_window": False},
        {"name": "Site", "url": "/", "new_window": True},
    ],

    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users-cog",

        "website.AboutPage": "fas fa-circle-info",
        "website.Service": "fas fa-screwdriver-wrench",
        "website.Project": "fas fa-diagram-project",
        "website.Industry": "fas fa-industry",
        "website.Job": "fas fa-briefcase",

        "website.BlogPost": "fas fa-newspaper",
        "website.Post": "fas fa-pen-nib",

        "website.ContactMessage": "fas fa-envelope",
        "website.PopUpMessage": "fas fa-bell",

    },

    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
}
