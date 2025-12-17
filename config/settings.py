from corsheaders.defaults import default_headers
from pathlib import Path
import os

import environ
from urllib.parse import urlparse, parse_qsl
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# initialize environment variables

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

# Multi-Factor Authentication settings
MFA_ISSUER = "S360 ERP"


# Application definition

SHARED_APPS = [
    'django_prometheus',
    'widget_tweaks',
    'django_user_agents',
    'cacheops',
    'rest_framework',
    'rest_framework.authtoken',
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # swagger
    'drf_yasg',
    'core.homepage',
    'core.multicpy',
    'core.security',
    'core.user',

    'users',
]

TENANT_APPS = [
    'django_prometheus',
    # important to handle tokens in tenants
    'rest_framework',
    'rest_framework.authtoken',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # swagger
    'drf_yasg',

    'core.billing',
    'core.dashboard',
    'core.login',
    'core.security',
    'core.network',
    'core.user',

    # own django apps
    'users',
    'log',
]

# INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
INSTALLED_APPS = [
    'widget_tweaks', 'django_user_agents', 'cacheops', 'rest_framework', 'rest_framework.authtoken', 'django_cleanup.apps.CleanupConfig', 'django.contrib.staticfiles', 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'core.homepage', 'core.multicpy', 'core.security', 'core.user', 'core.billing', 'core.dashboard', 'core.login', 'core.network',
    # 'django_crontab',
    # swagger
    'encrypted_model_fields',
    'drf_yasg',
    'users',
    'log',
]

MIDDLEWARE = [
    'core.multicpy.middleware.CustomMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # #### CORS headers: before CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',

    # ### Custom Middlewares
    'config.shared.middlewares.not_found_middleware.Custom404Middleware',
    'config.shared.middlewares.unauthorized_middleware.CustomUnauthorizedMiddleware',
    'config.shared.middlewares.front_version_middleware.FrontVersionMiddleware',

]

ROOT_URLCONF = 'config.urls'
PUBLIC_SCHEMA_URLCONF = 'config.public_urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

def get_db_config(environ_var='DATABASE_URL'):
    """Get Database configuration."""
    options = env.db(var=environ_var, default='sqlite:///db.sqlite3')
    if options.get('ENGINE') != 'django.db.backends.sqlite3':
        return options

    # This will allow use a relative to the project root DB path
    # for SQLite like 'sqlite:///db.sqlite3'
    if not options['NAME'] == ':memory:' and not os.path.isabs(options['NAME']):
        options.update({'NAME': os.path.join(BASE_DIR, options['NAME'])})

    return options


db_config = get_db_config()
# Quita la línea del backend de django_tenants
# db_config['ENGINE'] = 'django_tenants.postgresql_backend'

# Si tu DATABASE_URL ya contiene el ENGINE correcto, no hace falta cambiarlo
# Por ejemplo, para PostgreSQL normal:
db_config['ENGINE'] = 'django.db.backends.postgresql'


tmpPostgres = urlparse(os.getenv("DATABASE_URL"))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
        'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
    }
}

# DATABASE_ROUTERS = [
#    'django_tenants.routers.TenantSyncRouter',
#    'core.network.utils.db_routers.Router',
# ]

# Django-tenant-schemas

# TENANT_MODEL = 'multicpy.Scheme'

# TENANT_DOMAIN_MODEL = 'multicpy.Domain'

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


LANGUAGE_CODE = 'es-ec'

TIME_ZONE = 'America/Guayaquil'
USE_TZ = True

USE_I18N = True


USE_L10N = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


MEDIA_URL = '/media/'

# Auth

LOGIN_REDIRECT_URL = '/dashboard/'

LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = '/'

AUTH_USER_MODEL = 'users.Usuario'

# Sessions

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

SESSION_COOKIE_NAME = 'huaweioltconnect'

SESSION_COOKIE_AGE = 60 * 240

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# HTTP

SECURE_CROSS_ORIGIN_OPENER_POLICY = None

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# rest_framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    # global exception handler ---
    'EXCEPTION_HANDLER': 'config.shared.helpers.handle_rest_exception_drf_helper.handle_rest_exception_drf_helper',

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        # 'rest_framework_xml.renderers.XMLRenderer'
    ]
}

# Django-cacheops

# ### Cache
CACHES = {
    "default": {
        # "BACKEND": "django_redis.cache.RedisCache",
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Constants

CUSTOMER_GROUP = 2

DOMAIN = env.str('DOMAIN', default='localhost')

DEFAULT_SCHEMA = env.str('DEFAULT_SCHEMA', default='public')


# ### ### ### =================================================

# ### Swagger
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'SECURITY_REQUIREMENTS': [
        {
            'Token': []
        }
    ],
}


# ### CORS Origin ===========================
CORS_ALLOW_HEADERS = list(default_headers) + ['x-front-version']
CORS_ALLOWED_ORIGINS = env.str('CORS_ALLOWED_ORIGINS').split(',')

CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ["*"]


# ### MONITORING ----------------------------------
# 1) Añade django-prometheus
INSTALLED_APPS.insert(0, 'django_prometheus')

# 2) Middleware de métricas
MIDDLEWARE.insert(0, 'django_prometheus.middleware.PrometheusBeforeMiddleware')
MIDDLEWARE.append('django_prometheus.middleware.PrometheusAfterMiddleware')


# 4) Logging estructurado JSON para Promtail
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'standard': {
            'format': '[%(asctime)s | %(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
