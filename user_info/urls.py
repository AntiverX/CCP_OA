"""CCP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
from . import views

urlpatterns = [
    url(r'register', views.register, name="register"),
    url(r'login/', views.auth, name="login"),
    url(r'account_manage/', views.account_manage, name="account_manage"),
    url(r'user_info/', views.user_info_list, name="user_info"),
    url(r'user_info_list/', views.user_info_list, name="user_info_list"),
    url(r'user_info_manage/', views.user_info_manage, name="user_info_manage"),
    url(r'branch_manage/', views.branch_manage, name="branch_manage"),
    url(r'branch_info/', views.branch_info, name="branch_info"),
    url(r'valid/', views.valid, name="valid"),
    url(r'^$', views.index, name="info"),
]
