"""GeekParitySystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .views import home,login,regist,logout,get_invation_qrcode,wechat_login,check_login,send

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('product/', include(('product.urls','product'),namespace='product')),
    path('login', login, name='login'),
    path('regist', regist, name='regist'),
    path('logout', logout, name='logout'),
    path('get_invation_qrcode', get_invation_qrcode, name='get_invation_qrcode'),
    path('wechat_login', wechat_login, name='wechat_login'),
    path('check_login', check_login, name='check_login'),
    path('send/<str:uuid>/<str:NickName>/<str:UserName>/<str:invation_code>/<int:msg_type>', send, name='send_text'),
    # path('accounts/', include('django.contrib.auth.urls')),
]
