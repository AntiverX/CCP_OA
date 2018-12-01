from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from .models import User, CcpMember
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from CCP.settings import BASE_DIR
import random
import pandas as pd
from django.db import transaction


@login_required
def index(request):
    if request.method == "GET":
        if len(CcpMember.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)) != 0:
            ccp_member = CcpMember.objects.get(student_id=request.user.student_id, real_name=request.user.real_name)
        else:
            ccp_member = None
        context = {
            'user': request.user,
            'ccp_member': ccp_member,
            'select': "info",
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
            return HttpResponseRedirect("/")
        else:
            context['error'] = "用户名或密码错误"
            return render(request, "main_site/error.html", context=context)
    else:
        return render(request, 'user_info/login.html', context=context)


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
