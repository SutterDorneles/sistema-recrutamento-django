# Em seu_projeto/settings.py

from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# --- ALLOWED_HOSTS ATUALIZADO ---
ALLOWED_HOSTS = [
    'sutter.pythonanywhere.com',
    'www.rhori.com.br', # Lembre-se de substituir pelo seu domínio real
    'rhori.com.',     # E a versão sem 'www'
    '127.0.0.1',                 # Adicionado para permitir o acesso local
    'localhost',
]
# --- FIM DA ATUALIZAÇÃO ---


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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recrutamento.urls'

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

WSGI_APPLICATION = 'recrutamento.wsgi.application'

# Configuração da Base de Dados para Produção (MySQL)
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': '3306',
        }
    }
else:
    # Configuração para o seu computador (desenvolvimento)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração de E-mail e Segurança para Produção
if not DEBUG:
    # E-mail
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = config('SENDGRID_API_KEY')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

    # Segurança HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- CONFIGURAÇÕES DO DJANGO JAZZMIN (VERSÃO ESTÁVEL) ---
JAZZMIN_SETTINGS = {
    "site_title": "Painel RH Ori",
    "site_header": "RH Orientado",
    "welcome_sign": "Bem-vindo ao Painel de Gestão de RH",
    "theme": "flatly",
    
    
    # Adiciona o painel de "Ações Recentes" ao dashboard
    "show_recent_actions": True,
    
    # 1. Define a ordem exata dos modelos dentro da aplicação 'vagas'
    "order_with_respect_to": [
        "vagas.empresa", 
        "vagas.vaga", 
        "vagas.inscricao", 
        "vagas.candidato", 
        "vagas.funcionarioativo", 
        "vagas.funcionariodemitido", 
        "vagas.funcionariocomobservacao", 
        "vagas.funcionario",
        "vagas.pergunta",
        "vagas.respostacandidato"
    ],
    
    # 2. Renomeia a aplicação e define um ícone para o grupo
    "apps": {
        "vagas": {
            "name": "Gestão de Pessoas",
            "icon": "fas fa-users-cog",
        }
    },

    # 3. Define os ícones para cada modelo individualmente
    "icons": {
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "vagas.empresa": "far fa-building",
        "vagas.vaga": "fas fa-briefcase",
        "vagas.inscricao": "fas fa-file-signature",
        "vagas.candidato": "fas fa-user-plus",
        "vagas.funcionarioativo": "fas fa-user-check",
        "vagas.funcionariodemitido": "fas fa-user-times",
        "vagas.funcionariocomobservacao": "fas fa-user-tag",
        "vagas.funcionario": "fas fa-users",
        "vagas.pergunta": "fas fa-question-circle",
        "vagas.respostacandidato": "fas fa-poll-h",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False, # <-- Desativado para evitar conflitos
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
