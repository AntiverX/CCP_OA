from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from activity.models import Activity, ActivityRecord
from django.contrib.auth.decorators import login_required
from django.db import transaction
from CCP.settings import BASE_DIR
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import datetime
from CCP.common import is_teacher, is_gxh


@login_required
# 我的活动界面
def index(request):
    context = {
        "select": "activity",
        "select_1": "index",
    }
    if request.method == "GET":
        results = ActivityRecord.objects.filter(student_id=request.user.student_id)
        context['results'] = results
        return render(request, "activity/index.html", context=context)
    else:
        target_id = request.POST['target_id']
        selected_record = ActivityRecord.objects.get(id=target_id)
        if selected_record.activity_time > datetime.datetime.now():
            return JsonResponse(
                {
                    'title': "提交失败",
                    'content': "活动还未开始！"
                }
            )
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
                selected_record = ActivityRecord.objects.select_for_update().get(id=target_id)
                selected_activity = Activity.objects.select_for_update().get(activity_name=selected_record.activity_name)
                with transaction.atomic():
                    if selected_activity.close_time > datetime.datetime.now():
                        selected_record.delete()
                        selected_activity.present_person = selected_activity.present_person - 1
                        selected_activity.save()
                        return JsonResponse(
                            {
                                'title': "退出成功",
                                'content': "已退出该活动"
                            }
                        )
                    else:
                        return JsonResponse(
                            {
                                'title': "退出失败",
                                'content': "已经过了可退出时间"
                            }
                        )
            else:
                pass
        return HttpResponseRedirect("/activity/")


# 参加活动界面
@login_required
def joinActivity(request):
    context = {
        "select": "activity",
        "select_1": "joinActivity"
    }
    if request.method == "GET":
        results = Activity.objects.all()
        context['results'] = results
        return render(request, "activity/joinactivity.html", context=context)
    else:
        target_id = request.POST['target_id']
        target_activity = Activity.objects.get(id=target_id)
        # 参加活动
        if request.POST['action'] == "join":
            if datetime.datetime.now() > target_activity.close_time:
                return JsonResponse(
                    {
                        'title': "报名失败",
                        'content': "已经过了报名时间"
                    }
                )
            if len(ActivityRecord.objects.filter(real_name=request.user.real_name, student_id=request.user.student_id,
                                                 activity_name=target_activity.activity_name)) != 0:
                return JsonResponse(
                    {
                        'title': "报名失败",
                        'content': "你已参加此活动"
                    }
                )
            target_activity = Activity.objects.select_for_update().get(id=target_id)
            with transaction.atomic():
                if target_activity.present_person < target_activity.max_person:
                    target_activity.present_person = target_activity.present_person + 1
                    target_activity.save()
                else:
                    return JsonResponse(
                        {
                            'title': "报名失败",
                            'content': "参与人数已满"
                        }
                    )
            new_activity_record = ActivityRecord.objects.create(
                student_id=request.user.student_id,
                real_name=request.user.real_name,
                activity_name=Activity.objects.get(id=target_id).activity_name,
                activity_time=Activity.objects.get(id=target_id).activity_time,
                time_length=Activity.objects.get(id=target_id).time_length,
            )
            new_activity_record.save()
            return JsonResponse(
                {
                    'title': "报名成功",
                    'content': "你已经报名成功"
                }
            )


# 活动管理
@is_gxh
def activity_manage(request):
    context = {
        'select': 'activity_manage',
    }
    if request.method == 'GET':
        results = Activity.objects.all()
        context['results'] = results
        return render(request, "activity/activity_manage.html", context=context)
    else:
        if request.POST['type'] == "delete":
            existing_activity = Activity.objects.select_for_update().get(id=request.POST['id'])
            existing_activity_records = ActivityRecord.objects.select_for_update().filter(activity_name=existing_activity.activity_name)
            with transaction.atomic():
                existing_activity.delete()
                existing_activity_records.delete()
        else:
            if request.POST['id'] is not "":
                existing_activity = Activity.objects.select_for_update().get(id=request.POST['id'])
                existing_activity_records = ActivityRecord.objects.select_for_update().filter(activity_name=existing_activity.activity_name)
                with transaction.atomic():
                    existing_activity.activity_name = request.POST['activity_name']
                    existing_activity.time_length = request.POST['time_length']
                    existing_activity.max_person = request.POST['max_person']
                    existing_activity.activity_time = request.POST['activity_time']
                    existing_activity.close_time = request.POST['close_time']
                    existing_activity.person_in_charge = request.POST['person_in_charge']
                    existing_activity.content = request.POST['content']
                    for record in existing_activity_records:
                        record.activity_name = request.POST['activity_name']
                        record.time_length = request.POST['time_length']
                        record.activity_time = request.POST['activity_time']
                        record.close_time = request.POST['close_time']
                        record.save()
                    existing_activity.save()
            else:
                new_record = Activity(
                    activity_name=request.POST['activity_name'],
                    time_length=request.POST['time_length'],
                    close_time=request.POST['close_time'],
                    activity_time=request.POST['activity_time'],
                    max_person=request.POST['max_person'],
                    content=request.POST['content'],
                    publisher=request.POST['publisher'],
                    person_in_charge=request.POST['person_in_charge'],
                )
                new_record.save()
        return HttpResponse("success")


# 审计时长
def audit_activity_record(request):
    if request.method == "GET":
        context = {
            'activity_name': request.GET['activity_name'],
            'results': ActivityRecord.objects.filter(activity_name=request.GET['activity_name']),
        }
        return render(request, 'activity/audit_activity_record.html', context=context)
    else:
        target_id = request.POST['target_id']
        record = ActivityRecord.objects.get(id=target_id)
        record.is_ok = 1
        record.auditor = request.POST['auditor']
        record.save()
        return HttpResponse("success")


# 记录管理
def record_manage(request):
    context = {
        'select': 'record_manage',
        'select_1': "activity_record_manage",
    }
    if request.method == "GET":
        results = ActivityRecord.objects.filter(is_ok=False)
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
                try:
                    columns_list.remove("总时长")
                except:
                    pass
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
                            auditor = existing_activity.person_in_charge
                        except ObjectDoesNotExist:
                            activity_time = "1921-07-23"
                            time_length = row[column]
                            auditor = ""
                        new_activity_record = ActivityRecord.objects.create(
                            student_id=student_id,
                            real_name=real_name,
                            activity_name=column,
                            joinTime=activity_time,
                            activity_time=activity_time,
                            time_length=time_length,
                            is_ok=1,
                            auditor=auditor,

                        )
                        new_activity_record.save()
        return HttpResponseRedirect("/activity/record_manage")


# 获取单次活动信息
@csrf_exempt
@login_required
def get_activity(request):
    if request.method == "POST":
        id = request.POST['id']
        existing_activity = Activity.objects.get(id=id)
        return JsonResponse(
            {
                "activity_name": existing_activity.activity_name,
                "time_length": existing_activity.time_length,
                "max_person": existing_activity.max_person,
                "activity_time": existing_activity.activity_time.strftime("%Y-%m-%d %H:%M"),
                "close_time": existing_activity.close_time.strftime("%Y-%m-%d %H:%M"),
                "person_in_charge": existing_activity.person_in_charge,
                "content": existing_activity.content,
            }
        )


# 获取活动参加记录
@login_required
@csrf_exempt
def get_activity_record(request):
    if request.method == "POST":
        id = request.POST['id']
        activity_name = Activity.objects.get(id=id).activity_name
        if len(ActivityRecord.objects.filter(activity_name=activity_name, student_id=request.user.student_id)):
            return JsonResponse(
                {
                    "join": "yes",
                }
            )
        else:
            return JsonResponse(
                {
                    "join": "no",
                }
            )
