from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Setting
from CCP.common import is_gxh
from django.core.management import call_command
from django.contrib.sessions.models import Session

context = {}


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/user_info")
    else:
        context['user'] = request.user
        context['select'] = 'index'
        return render(request, "main_site/index.html", context=context)


@login_required
def manage(request):
    context = {}
    context['select'] = 'manage'
    context['select_1'] = 'setting'
    return render(request, "main_site/manage.html", context=context)


@is_gxh
def setting(request):
    context = {
        'select': "setting",
        "select_1": ""
    }
    if request.method == "GET":
        is_closed = Setting.objects.get(setting_name="is_closed")
        context['is_closed'] = is_closed.setting_value
        return render(request, "main_site/manage.html", context=context)
    else:
        is_closed = request.POST['is_closed']
        existing_is_closed = Setting.objects.get(setting_name="is_closed")
        existing_is_closed.setting_value = is_closed
        existing_is_closed.save()
        if existing_is_closed.setting_value == "True":
            [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_hash') != request.user.get_session_auth_hash()]
        return HttpResponseRedirect("/system/setting")
