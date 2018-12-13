from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from .models import User, CcpMember, Branch
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from CCP.settings import BASE_DIR
import random
import pandas as pd
from django.db import transaction
from journey.models import DocumentInfo, CourseInfo
from dateutil.relativedelta import *

import datetime

@login_required
def index(request):
    if request.method == "GET":
        if len(CcpMember.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)) != 0:
            ccp_member = CcpMember.objects.get(student_id=request.user.student_id, real_name=request.user.real_name)
        else:
            ccp_member = None
        if len(DocumentInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="入党志愿书")) != 0:
            date_1 = DocumentInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="入党志愿书")[0].date
            birthday = ccp_member.id_number[6:-8] + "-" + ccp_member.id_number[10:-6] + "-" + ccp_member.id_number[12:-4]
            age = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            if age.year - datetime.datetime.now().year >= 18 and age.month - datetime.datetime.now().month >=0 and age.day - datetime.datetime.now().day >=0:
                date_2 = date_1 + relativedelta(months=1)
                date_5 = date_1 + relativedelta(years=1)
            else:
                date_2 = ""
                date_5 = ""
        else:
            date_1 = ""
            date_2 = ""
            date_5 = ""
        if len(CourseInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name,
                                         name="院党课")) != 0:
            date_3 = CourseInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="院党课")[0].date
        else:
            date_3 = ""
        if len(CourseInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name,
                                         name="校党课")) != 0:
            date_4 = CourseInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="校党课")[0].date
        else:
            date_4 = ""
        context = {
            'user': request.user,
            'ccp_member': ccp_member,
            'select': "info",
            'date_1': date_1,
            'date_2': date_2,
            'date_3': date_3,
            'date_4': date_4,
            'date_5': date_5,
        }
        return render(request, "user_info/index.html", context=context)
    else:
        real_name = request.POST['real_name']
        student_id = request.POST['student_id']
        email = request.POST['email']
        file = request.FILES.get('file')
        if file is not None:
            path = "photo/" + student_id + " - " + str(random.randint(1, 1000)) + ".jpg"
            file_name = BASE_DIR + "/static/" + path
            with open(file_name.encode(), "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            request.user.photo_path = path
        request.user.real_name = real_name
        request.user.student_id = student_id
        request.user.email = email
        request.user.save()
        return HttpResponseRedirect("/user_info")


def auth(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/user_info")
        else:
            context['error'] = "用户名或密码错误"
            return render(request, "main_site/error.html", context=context)
    else:
        return render(request, 'user_info/login.html', context=context)


def deauth(request):
    logout(request)
    return HttpResponseRedirect("/")


def register(request):
    context = {}
    if request.method == "GET":
        return render(request, 'user_info/register.html', context=context)
    else:
        username = request.POST['username']
        e_mail = request.POST['email']
        password = request.POST['password']
        real_name = request.POST['real_name']
        student_id = request.POST['student_id']
        new_user = User.objects.create_user(
            username=username,
            email=e_mail,
            password=password,
            real_name=real_name,
            student_id=student_id,
        )
        new_user.save()
        return HttpResponseRedirect("/user_info/login")


@login_required
def account_manage(request):
    if request.method == "GET":
        context = {}
        context['select'] = "manage"
        context['results'] = User.objects.all()
        return render(request, "user_info/account_manage.html", context=context)
    else:
        if request.POST['btn'] == "delete":
            target_id = request.POST['target_id']
            user = User.objects.get(id=target_id)
            user.delete()
        return HttpResponseRedirect("http://127.0.0.1:8000/user_info/account_manage/")


# 上传党员信息
@login_required
def user_info_manage(request):
    context = {}
    if request.method == "GET":
        context['select'] = "manage"
        context['results'] = CcpMember.objects.all()
        return render(request, "user_info/user_info_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        if file is not None:
            with transaction.atomic():
                CcpMember.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "user_info.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name)
                for index, row in data.iterrows():
                    new_ccp_member = CcpMember.objects.create(
                        student_id=row['学号'],
                        real_name=row['姓名'],
                        branch=row['党支部'],
                        current_state=row['面貌'],
                        phone_number=row['联系电话'],
                        date=row['入党时间'],
                        sponsor=row['入党介绍人'],
                        id_number=row['身份证号'],
                        related_class=row['班级'],
                        tutor=row['导师']
                    )
                    new_ccp_member.save()
                return HttpResponseRedirect("/user_info/user_info_manage/")
        else:
            new_ccp_member = CcpMember.objects.create(
                student_id=request.POST['student_id'],
                real_name=request.POST['real_name'],
                branch=request.POST['branch'],
                current_state=request.POST['current_state'],
                phone_number=request.POST['phone_number'],
                date=request.POST['date'],
                sponsor=request.POST['sponsor'],
            )
            new_ccp_member.save()
            return HttpResponseRedirect("/user_info/user_info_manage/")


# 上传党员信息
@login_required
def branch_manage(request):
    context = {}
    if request.method == "GET":
        context['select'] = "manage"
        context['results'] = Branch.objects.all()
        return render(request, "user_info/branch_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        if file is not None:
            with transaction.atomic():
                Branch.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "branch.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name)
                for index, row in data.iterrows():
                    new_ccp_member = Branch.objects.create(
                        branch_name=row['支部名称'],
                        branch_secretary_0=row['支部书记'],
                        branch_secretary_1=row['组织委员'],
                        branch_secretary_2=row['宣传委员'],
                    )
                    new_ccp_member.save()
                return HttpResponseRedirect("/user_info/branch_manage/")
        else:
            new_ccp_member = CcpMember.objects.create(
                branch_name=request.POST['student_id'],
                branch_secretary_0=request.POST['real_name'],
                branch_secretary_1=request.POST['branch'],
                branch_secretary_2=request.POST['current_state'],
            )
            new_ccp_member.save()
            return HttpResponseRedirect("/user_info/branch_manage/")
