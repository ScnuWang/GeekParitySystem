"""
Django settings for GeekParitySystem project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$28yj#us=%nq==62e+mr%(-wrh90ndkhm#d#w$-09)whdt5kbt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'product.apps.ProductConfig',
    'geekuser.apps.GeekuserConfig',
    'jieba'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GeekParitySystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'GeekParitySystem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# NAME 是指的数据库名称
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'geekparity',
        'USER': 'root',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'mongo_db':{
       'ENGINE': None,
    },
}
from mongoengine import connect
connect('geekparity',host='127.0.0.1',port = 27017)  # 连接的数据库名称


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# 用于为了部署搜集静态文件
#STATIC_ROOT = "/var/parity.geekview.cn/static/"

# 静态文件目录路径  : 需要添加这个在能使用智能提示静态文件的路径
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]

# 使用自己的GeekUser模型:geekuser表示APP的名称
AUTH_USER_MODEL = 'geekuser.GeekUser'

# 多数据库路由配置
DATABASE_ROUTERS = ['GeekParitySystem.dbrouter.AuthRouter',]
# 分词关键字保存路径
MY_SEG_DICT_PATH = os.path.join(BASE_DIR,'static/keyword/product.txt')
# 分类文件路径
MY_CATEGORY_PATH = os.path.join(BASE_DIR,'static/init/category.json')
# 邀请码二维码存放路径
QRCODE_IMAGE_PATH = os.path.join(BASE_DIR,'static/qrcode/')
# 图片存放路径
IMAGE_PATH = os.path.join(BASE_DIR,'static/image/')
# 平台编号字典
ENABLE_WEBSITE_DIC = {'xiaomi':1,'wangyi':2}