from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.shortcuts import render
from activity.models import Activity, ActivityRecord
from django.contrib.auth.decorators import login_required
from django.db import transaction
import random
from CCP.settings import BASE_DIR
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

@login_required
# 测试用活动界面
def index(request):
    context = {
        "select": "activity",
        "select_1": "index",
    }
    if request.method == "GET":
        results = ActivityRecord.objects.filter(student_id="1120141123")
        context['results'] = results
        return render(request, "activity/index.html", context=context)
    else:
        target_id = request.POST['target_id']
        selected_record = ActivityRecord.objects.get(id=target_id)
        file = request.FILES.get('proof')
        if file is not None:
            path = "/static/file/" + request.user.student_id + " - " + selected_record.activity_name + "." + file.name.split(".")[1]
            file_name = BASE_DIR + path
            with open(file_name.encode(), "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            selected_record.proof = path
            selected_record.save()
        else:
            # 用户退出活动
            if request.POST['btn'] == "quit":
                activity_name = selected_record.activity_name
                selected_record.delete()
                with transaction.atomic():
                    selected_activity = Activity.objects.get(activity_name=activity_name)
                    selected_activity.present_person = selected_activity.present_person - 1
                    selected_activity.save()
            else:
                pass
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
        return render(request, "activity/activity_manage.html", context=context)
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
            context['return_url'] = "activity"
            return render(request, 'main_site/error.html', context=context)
        with transaction.atomic():
            target_activity = Activity.objects.get(id=target_id)
            if target_activity.present_person < target_activity.max_person:
                target_activity.present_person = target_activity.present_person + 1
                target_activity.save()
            else:
                context['error'] = "参与人数已满"
                context['return_url'] = "activity"
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


def audit_record(request):
    context = {
        'select': 'manage',
    }
    if request.method == "GET":
        results = ActivityRecord.objects.filter(is_ok="否")
        context['results'] = results
        context['auditor'] = request.user.real_name
        return render(request, "activity/record_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        # 上传活动时长记录
        if file is not None:
            with transaction.atomic():
                if request.POST['is_cover'] == "1":
                    ActivityRecord.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "activity_record.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name)
                columns_list = data.columns.values.tolist()
                columns_list.remove("学号")
                columns_list.remove("姓名")
                columns_list.remove("总时长")
                for index, row in data.iterrows():
                    student_id = row["学号"]
                    real_name = row["姓名"]
                    for column in columns_list:
                        # 如果时长是0，就不再添加了
                        if row[column] == 0:
                            continue
                        try:
                            existing_activity = Activity.objects.get(activity_name=column)
                            activity_time = existing_activity.activity_time
                            time_length = existing_activity.time_length
                        except ObjectDoesNotExist:
                            activity_time = "1921-07-23"
                            time_length = row[column]
                        new_activity_record = ActivityRecord.objects.create(
                            student_id=student_id,
                            real_name=real_name,
                            activity_name=column,
                            joinTime=activity_time,
                            activity_time=activity_time,
                            time_length=time_length,
                            is_ok=True,
                            auditor="",

                        )
                        new_activity_record.save()
        else:
            target_id = request.POST['target_id']
            auditor = request.POST['auditor']
            selected_record = ActivityRecord.objects.get(id=target_id)
            selected_record.auditor = auditor
            selected_record.is_ok = "是"
            selected_record.save()
        return HttpResponseRedirect("/activity/manage/audit_record")

@csrf_exempt
def get_activity(request):
    if request.method == "POST":
        id = request.POST['id']
        existing_activity = Activity.objects.get(id=id)
        return JsonResponse(
            {
                "content":existing_activity.content,
            }
        )
