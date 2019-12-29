# -*- coding: utf-8 -*-
"""
Django settings for nuesoft-system project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ
# import redisco



ROOT_DIR = environ.Path(__file__) - 3  # (nuesoft-system/config/settings/common.py - 3 = nuesoft-system/)
APPS_DIR = ROOT_DIR.path('nuesoft-system')

# 从 .env 文件中读取相关的环境配置信息
env = environ.Env()
env.read_env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Admin
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    # 'ws4redis',  # django-websocket
)

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'nuesoft-system.common.apps.CommonConfig',#通用工具
    'nuesoft-system.vanilla.apps.VanillaConfig', #通用视图
    'nuesoft-system.sysadmin.apps.SysadminConfig',  # sysamdin
    'nuesoft-system.scriptmgr.apps.ScriptmgrConfig',#脚本管理
    'nuesoft-system.zabbixmgr.apps.ZabbixmgrConfig',#zabbix
    'nuesoft-system.dialing.apps.DialingConfig',#自动拨测
    'nuesoft-system.cabinetmgr.apps.CabinetmgrConfig',#机柜管理
    'nuesoft-system.filemanage.apps.FilemanageConfig',#文件管理

    # Your stuff: custom apps go here
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installeed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 登录
    'nuesoft-system.sysadmin.middleware.QtsAuthenticationMiddleware',#登录拦截
    'nuesoft-system.sysadmin.middleware.SysCatchException', #异常抓取
    'nuesoft-system.sysadmin.middleware.SysLogSaveMiddleware',#系统日志
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
# 存放 sites migrations 的目录
MIGRATION_MODULES = {
    'sites': 'nuesoft-system.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', True)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', default='django.core.mail.backends.smtp.EmailBackend')
# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'neusoft',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
        'CHARSET': 'utf8',
    },
    # 'zabbixdb': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'zabbix',
    #     'USER': 'zabbix',
    #     'PASSWORD': '123.com',
    #     'HOST': '192.168.231.100',
    #     'PORT': '3306',
    #     'CHARSET': 'utf8',
    # },
    # 'zabbixdb': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'zabbix',
    #     'USER': 'dongruan2',
    #     'PASSWORD': 'Gz@2018dr',
    #     'HOST': '188.1.184.251',
    #     'PORT': '3306',
    #     'CHARSET': 'utf8',
    # },
    # 'otherdb': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'mycontract_db',
    #     'USER': 'gzqridc',
    #     'PASSWORD': 'gzqrIDC@123',
    #     'HOST': '183.240.111.18',
    #     'PORT': '3306',
    #     'CHARSET': 'utf8',
    # },
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASE_ROUTERS = ['config.settings.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    # example:
    #'app_name':'database_name',
    'app1': 'zabbixdb',
}
# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'zh-hans'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # 'ws4redis.context_processors.default',
                'nuesoft-system.sysadmin.views.globar_setting',
                # 'nuesoft-system.sysadmin.views.login_data',
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'



# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = 'sysadmin.SysUser'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'nuesoft-system.sysadmin.models.CustomAuth')

# django-compressor
# ------------------------------------------------------------------------------
INSTALLED_APPS += ("compressor",)
STATICFILES_FINDERS += ("compressor.finders.CompressorFinder",)

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

