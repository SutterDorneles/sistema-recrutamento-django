# Em seu_projeto/settings.py

from pathlib import Path
# Importamos a função 'config' da biblioteca decouple
from decouple import config
import os # Adicionado para STATIC_ROOT

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES DE SEGURANÇA ---

# A SECRET_KEY agora é lida do ficheiro .env
# Se não for encontrada, o Django não irá iniciar (o que é bom para a segurança)
SECRET_KEY = config('SECRET_KEY')

# O DEBUG é lido do .env. O 'default=False' garante que, em produção,
# onde o ficheiro .env pode não existir, o DEBUG seja FALSO por segurança.
# O 'cast=bool' converte o texto "True" ou "False" para o tipo booleano correto.
DEBUG = config('DEBUG', default=False, cast=bool)

# Em produção, esta lista precisa de conter o seu domínio (ex: 'www.meusite.com').
# Por agora, vamos permitir o endereço local e, futuramente, adicionaremos o do site online.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vagas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Adicionado o middleware do Whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recrutamento.urls' # Ajuste 'recrutamento' para o nome da sua pasta de projeto

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'recrutamento.wsgi.application' # Ajuste 'recrutamento' para o nome da sua pasta de projeto


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
# Pasta onde o collectstatic irá juntar todos os ficheiros estáticos para produção
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Configuração de armazenamento do Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files (Uploads dos usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração de E-mail para Desenvolvimento
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Configurações do Django Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Painel de Recrutamento",
    "site_header": "Recrutamento",
    "welcome_sign": "Bem-vindo ao Painel de Recrutamento",
    "theme": "flatly",
    "UI_enhancements": {
        "border_radius": "0.5rem",
    },
}
