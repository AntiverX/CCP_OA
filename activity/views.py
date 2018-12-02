from django.http import HttpResponseRedirect
from django.shortcuts import render
from activity.models import Activity, ActivityRecord
from django.contrib.auth.decorators import login_required
from django.db import transaction


@login_required
# 显示我的活动
def index(request):
    context = {
        "select": "activity"
    }
    if request.method == "GET":
        results = ActivityRecord.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)
        context['results'] = results
        return render(request, "activity/index.html", context=context)
    else:
        target_id = request.POST['target_id']
        selected_record = ActivityRecord.objects.get(id=target_id)
        activity_name = selected_record.activity_name
        selected_record.delete()
        with transaction.atomic():
            selected_activity = Activity.objects.get(activity_name=activity_name)
            selected_activity.present_person = selected_activity.present_person - 1
            selected_activity.save()
        return HttpResponseRedirect("/activity/")


# 管理员添加活动
@login_required
def manage(request):
    context = {
        'select': 'manage',
    }
    if request.method == 'GET':
        results = Activity.objects.all()
        context['results'] = results
        return render(request, "activity/manage.html", context=context)
    else:
        activity_name = request.POST['activity_name']
        time_length = request.POST['time_length']
        max_person = request.POST['max_person']
        activity_time = request.POST['activity_time']
        close_time = request.POST['close_time']
        publisher = request.POST['publisher']
        new_activity = Activity.objects.create(
            activity_name=activity_name,
            time_length=time_length,
            max_person=max_person,
            activity_time=activity_time,
            close_time=close_time,
            publisher=publisher,
        )
        new_activity.save()
        return HttpResponseRedirect("/activity/manage/")


# 用户参加活动
@login_required
def joinActivity(request):
    context = {
        "select": "activity"
    }
    if request.method == "GET":
        results = Activity.objects.all()
        context['results'] = results
        return render(request, "activity/attend_activity.html", context=context)
    else:
        target_id = request.POST['target_id']
        target_activity = Activity.objects.get(id=target_id)
        if len(ActivityRecord.objects.filter(real_name=request.user.real_name, student_id=request.user.student_id,
                                             activity_name=target_activity.activity_name)) != 0:
            context['error'] = "你已参加此活动"
            return render(request, 'main_site/error.html', context=context)
        with transaction.atomic():
            target_activity = Activity.objects.get(id=target_id)
            if target_activity.present_person < target_activity.max_person:
                target_activity.present_person = target_activity.present_person + 1
                target_activity.save()
            else:
                context['error'] = "参与人数已满"
                return render(request, 'main_site/error.html', context=context)
        new_activity_record = ActivityRecord.objects.create(
            student_id=request.user.student_id,
            real_name=request.user.real_name,
            activity_name=Activity.objects.get(id=target_id).activity_name,
            activity_time=Activity.objects.get(id=target_id).activity_time,
            time_length=Activity.objects.get(id=target_id).time_length,
        )
        new_activity_record.save()
        return HttpResponseRedirect("/activity")
