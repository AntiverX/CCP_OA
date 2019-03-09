from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Setting, Semester
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
        context['semesters'] = Semester.objects.all()
        return render(request, "main_site/manage.html", context=context)
    else:
        is_closed = request.POST['is_closed']
        existing_is_closed = Setting.objects.get(setting_name="is_closed")
        existing_is_closed.setting_value = is_closed
        existing_is_closed.save()
        if existing_is_closed.setting_value == "True":
            [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_hash') != request.user.get_session_auth_hash()]
        return HttpResponseRedirect("/system/setting")


@is_gxh
def semester(request):
    if request.method == "GET":
        semester = Semester.objects.all().order_by('-semester_start_time')
        return JsonResponse(
            semester
        )
    elif request.method == "POST":
        if request.POST['type'] == "add" or request.POST['type'] == "modify":
            check_start_time = Semester.objects.filter(semester_end_time__gte=request.POST['semester_start_time']).filter(semester_end_time__lte=request.POST['semester_start_time'])
            check_end_time = Semester.objects.filter(semester_end_time__gte=request.POST['semester_end_time']).filter(semester_end_time__lte=request.POST['semester_end_time'])
            if request.POST['type'] == "add":
                target_id = ""
            else:
                target_id = request.POST['target_id']
            if len(check_start_time) > 0:
                if check_start_time[0].id != target_id:
                    return JsonResponse(
                        {
                            'title': "添加或修改失败",
                            'content': "日期冲突",
                        }
                    )

            if len(check_end_time) > 0:
                if check_end_time[0].id != target_id:
                    return JsonResponse(
                        {
                            'title': "添加或修改失败",
                            'content': "日期冲突",
                        }
                    )
            else:
                pass
        if request.POST['type'] == "add":
            new_semester = Semester(
                semester_name=request.POST['semester_name'],
                semester_start_time=request.POST['semester_start_time'],
                semester_end_time=request.POST['semester_end_time'],
            )
            new_semester.save()
            return JsonResponse(
                {
                    'title': "添加成功",
                    'content': "新学期添加成功"
                }
            )
        elif request.POST['type'] == "modify":
            target_id = request.POST['target_id']
            existing_record = Semester.objects.get(id=target_id)
            existing_record.semester_name = request.POST['semester_name']
            existing_record.semester_start_time = request.POST['semester_start_time']
            existing_record.semester_end_time = request.POST['semester_end_time']
            existing_record.save()
            return JsonResponse(
                {
                    'title': "修改成功",
                    'content': "新学期修改成功"
                }
            )
        elif request.POST['type'] == "delete":
            target_id = request.POST['target_id']
            existing_record = Semester.objects.get(id=target_id)
            existing_record.delete()
            return JsonResponse(
                {
                    'title': "删除成功",
                    'content': "新学期删除成功"
                }
            )
