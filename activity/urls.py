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
from django.conf.urls import url, include, re_path

# from django.contrib import admin


from activity import views

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^add_activity$", views.add_activity, name="add_activity"),
    re_path(r"^get_activity$", views.get_activity),
    re_path(r"^get_activity_record$", views.get_activity_record),
    re_path(r"^activity_manage", views.activity_manage, name="activity_manage"),
    re_path(r"^audit_activity_record/", views.audit_activity_record,name="audit_activity_record"),
    re_path(r"^audit_activity_record/(?P<activity_name>[\w-]+)/$", views.audit_activity_record),

    re_path(r"joinActivity", views.joinActivity, name="joinActivity"),
    re_path(r"^record_manage$", views.audit_record, name="record_manage"),
    re_path(r"^activity_record_manage$", views.activity_record_manage, name="activity_record_manage"),
    re_path(r"^$", views.index, name="activity"),
]
