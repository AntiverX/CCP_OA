from django.http import HttpResponseRedirect
from django.shortcuts import render
from activity.models import Activity, ActivityRecord
from django.contrib.auth.decorators import login_required
from django.db import transaction


@login_required
def index(request):
    context = {
        "select": "activity"
    }
    results = ActivityRecord.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)
    context['results'] = results
    return render(request, "activity/index.html", context=context)


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
        return render(request, "activity/activity.html", context=context)
    else:
        target_id = request.POST['target_id']
        target_activity = Activity.objects.get(id=target_id)
        if len(ActivityRecord.objects.filter(real_name=request.user.real_name,student_id=request.user.student_id,activity_name=target_activity.activity_name)) != 0:
            context['error'] = "你已参加此活动"
            return render(request,'main_site/error.html',context=context)
        with transaction.atomic():
            target_activity = Activity.objects.get(id=target_id)
            if target_activity.present_person < target_activity.max_person:
                target_activity.present_person = target_activity.present_person + 1
            target_activity.save()
        new_activity_record = ActivityRecord.objects.create(
            student_id=request.user.student_id,
            real_name=request.user.real_name,
            activity_name=Activity.objects.get(id=target_id).activity_name,
            activity_time=Activity.objects.get(id=target_id).activity_time,
            time_length=Activity.objects.get(id=target_id).time_length,
        )
        new_activity_record.save()
        return HttpResponseRedirect("/activity")


@login_required
def activityAdd(request):
    context = {
        "select": "activity"
    }
    if request.method == "GET":
        return render(request, "activity/add.html", context=context)
    else:
        activityName = request.POST['activityName']
        newActivity = Activity.objects.create(
            activityName=activityName
        )
        newActivity.save()
        print(activityName)
        return HttpResponseRedirect("/activity/manage")


@login_required
def activityAll(request):
    """"""
    context = {
        "select": "activity",
        "activities": Activity.objects.all()
    }
    return render(request, "activity/manage.html", context=context)
