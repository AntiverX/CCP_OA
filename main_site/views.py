from django.shortcuts import render, HttpResponseRedirect
from user_info.models import User
from django.contrib.auth.decorators import login_required

context = {}


def index(request):
    context['user'] = request.user
    context['select'] = 'index'
    return render(request, "main_site/index.html", context=context)


def manage(request):
    context = {}
    context['select'] = 'manage'
    context['manage'] = 1
    return render(request, "main_site/manage.html", context=context)


def setting(request):
    context = {}
    context['select'] = 'manage'
    return render(request, "main_site/manage.html", context=context)
