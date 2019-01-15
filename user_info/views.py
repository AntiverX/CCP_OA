from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .models import User, CcpMember, Branch
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from CCP.settings import BASE_DIR
import random
import pandas as pd
from django.db import transaction
from journey.models import DocumentInfo, CourseInfo
from dateutil.relativedelta import *
from CCP.common import is_teacher, is_gxh, is_secretary
import re
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from main_site.models import Setting
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers


@login_required
def index(request):
    if request.user.is_gxh or request.user.is_teacher:
        return HttpResponseRedirect("http://ccp.ibiter.org/system/setting")
    if request.method == "GET":
        if len(CcpMember.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)) != 0:
            ccp_member = CcpMember.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)[0]
        else:
            ccp_member = None

        # 得到申请入党日期date_1
        if ccp_member is not None:
            date_1 = ccp_member.application_date
        elif len(DocumentInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="入党志愿书")) != 0:
            date_1 = DocumentInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name, name="入党志愿书")[0].date
        else:
            date_1 = ""

        if ccp_member is not None:
            # 计算年龄
            birthday = ccp_member.id_number[6:-8] + "-" + ccp_member.id_number[10:-6] + "-" + ccp_member.id_number[12:-4]
            age = datetime.datetime.strptime(birthday, '%Y-%m-%d')

            # date_2为推优日期 date_5为列为发展对象日期
            if datetime.datetime.now().year - age.year > 18:
                date_2 = date_1 + relativedelta(months=1)
                date_5 = date_1 + relativedelta(years=1)
            elif age.year - datetime.datetime.now().year == 18 and age.month - datetime.datetime.now().month >= 0 and age.day - datetime.datetime.now().day >= 0:
                date_2 = date_1 + relativedelta(months=1)
                date_5 = date_1 + relativedelta(years=1)
            else:
                date_2 = ""
                date_5 = ""
        else:
            date_2 = ""
            date_5 = ""

        # date_3是院党课通过时间
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

        # 获取支部名称
        if ccp_member is None:
            branch_name = ""
        elif ccp_member.branch != "":
            branch_name = ccp_member.branch
        # 根据导师获取支部名称
        elif ccp_member.tutor != "":
            try:
                branch = Branch.objects.get(tutor__contains=ccp_member.tutor)
                branch_name = branch.branch_name
            except:
                branch_name = ""
        # 根据班级获取支部名称
        else:
            try:
                branch = Branch.objects.get(tutor__contains=ccp_member.related_class)
                branch_name = branch.branch_name
            except:
                branch_name = ""
        context = {
            'user': request.user,
            'ccp_member': ccp_member,
            'select': "info",
            'date_1': date_1,
            'date_2': date_2,
            'date_3': date_3,
            'date_4': date_4,
            'date_5': date_5,
            'branch': branch_name
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


# 登录
def auth(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        existing_is_closed = Setting.objects.get(setting_name="is_closed")
        if user is not None:

            if user.is_gxh or user.is_teacher:
                login(request, user)
                return HttpResponseRedirect("/system/setting")
            else:
                if existing_is_closed.setting_value == "True":
                    context['error'] = "网站正在维护"
                    context['return_url'] = "index"
                    return render(request, "main_site/error.html", context=context)
                else:
                    login(request, user)
                    return HttpResponseRedirect("/user_info")
        else:
            context['error'] = "用户名或密码错误"
            context['return_url'] = "index"
            return render(request, "main_site/error.html", context=context)
    else:
        return HttpResponseRedirect("/")


# 注销
@login_required
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
        if len(User.objects.filter(student_id=student_id)) != 0:
            context['error'] = "你的党员信息已经有账号绑定，用户名是{},如有问题请联系共学会".format(User.objects.get(student_id=student_id).username)
            context['return_url'] = "index"
            return render(request, "main_site/error.html", context=context)
        else:
            new_user = User.objects.create_user(
                username=username,
                email=e_mail,
                password=password,
                real_name=real_name,
                student_id=student_id,
            )
            new_user.save()
            return HttpResponseRedirect("/")


# 账号管理
@is_gxh
def account_manage(request):
    if request.method == "GET":
        context = {
            'select': "account_manage",
            'results': User.objects.all(),
        }
        return render(request, "user_info/account_manage.html", context=context)
    else:
        if request.POST['btn'] == "delete":
            target_id = request.POST['target_id']
            user = User.objects.get(id=target_id)
            user.delete()
        else:
            target_id = request.POST['target_id']
            user = User.objects.get(id=target_id)
            user.is_admin = request.POST['is_admin']
            user.is_gxh = request.POST['is_gxh']
            user.is_teacher = request.POST['is_teacher']
            user.is_secretary = request.POST['is_secretary']
            user.save()
        return HttpResponseRedirect("/user_info/account_manage/")


# 党员列表
@is_gxh
def user_info_list(request):
    context = {}
    if request.method == "GET":
        context['select'] = "user_info"
        context['select_1'] = "user_info_list"
        context['results'] = CcpMember.objects.all()[0:10]
        return render(request, "user_info/user_info_list.html", context=context)


# 获得指定数量的党员列表
@csrf_exempt
@is_gxh
def get_ccp_member_list(request):
    if request.method == "POST":
        page = request.POST['page']
        results = CcpMember.objects.all()[10 * (int(page) - 1):10 * int(page)]
        results_dict = []
        for result in results:
            results_dict.append({
                "student_id": result.student_id,
                "real_name": result.real_name,
                "related_class": result.related_class,
                "tutor": result.tutor,
                "id_number": result.id_number,
                "phone_number": result.phone_number,
                "current_state": result.current_state,
                "date": result.date,
                "sponsor": result.sponsor,
            })
        return JsonResponse(results_dict, safe=False)


# 上传党员信息
@is_teacher
def user_info_manage(request):
    # 用来匹配日期的函数
    def parse_date(date: str, default="1921-07-23") -> str:
        if pd.isna(date):
            date = default
        else:
            _date = re.findall(r"[0-9]{4}.[0-9]{1,2}.[0-9]{1,2}", date)
            if len(_date) == 0:
                date = default
            else:
                try:
                    date = datetime.datetime.strptime(_date[0], "%Y-%m-%d")
                except ValueError:
                    try:
                        date = datetime.datetime.strptime(_date[0], "%Y/%m/%d")
                    except ValueError:
                        try:
                            date = datetime.datetime.strptime(_date[0], "%Y.%m.%d")
                        except ValueError:
                            try:
                                date = datetime.datetime.strptime(_date[0], "%Y年%m月%d")
                            except:
                                date = default
        return date

    context = {}
    if request.method == "GET":
        context['select'] = "user_info"
        context['select_1'] = "user_info_manage"
        return render(request, "user_info/user_info_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        if file is not None:
            with transaction.atomic():
                if request.POST['is_cover'] == "1":
                    CcpMember.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "user_info.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name, converters={'班号': str, '入党日期': str, '申请入党时间': str})
                columns_list = data.columns.values
                for index, row in data.iterrows():
                    # 如果记录重复，则提交的记录为党员是积极分子时的记录
                    if len(CcpMember.objects.filter(student_id=row['学号'])) != 0:
                        existing_reocrd = CcpMember.objects.get(student_id=row['学号'])
                        if "申请入党时间" in columns_list:
                            date = parse_date(row["申请入党时间"])
                        else:
                            date = "1921-07-23"
                        existing_reocrd.application_date = date
                        try:
                            existing_reocrd.save()
                        except:
                            context = {
                                'error': "申请入党时间错误，入党时间内容为：{}，格式为：{}".format(row["申请入党时间"], type(row["申请入党时间"])),
                                'return_url': "user_info_manage",
                            }
                            return render(request, "main_site/error.html", context=context)
                        continue

                    # 班号
                    if "班号" in columns_list:
                        related_class = "" if pd.isna(row['班号']) else row['班号']
                    else:
                        related_class = "" if pd.isna(row['班级']) else row['班级']

                    # 党员类型
                    if "党员类型" in columns_list:
                        current_state = "" if pd.isna(row['党员类型']) else row['党员类型']
                    else:
                        current_state = "积极分子"

                    # 入党时间
                    if "入党日期" in columns_list:
                        date = parse_date(row["入党日期"])
                    else:
                        date = "1921-07-23"

                    # 申请入党时间
                    if "申请入党日期" in columns_list:
                        application_date = parse_date(row["申请入党日期"])
                    else:
                        application_date = "1921-07-23"

                    # 导师
                    if "导师" in columns_list:
                        tutor = "" if pd.isna(row['导师']) else row['导师']
                    else:
                        tutor = ""
                    phone_number = "" if pd.isna(row['联系方式']) else row['联系方式']
                    id_number = "" if pd.isna(row['身份证号码']) else row['身份证号码']

                    branch = "" if pd.isna(row['对应的党支部']) else row['对应的党支部']
                    try:
                        new_ccp_member = CcpMember.objects.create(
                            student_id=row['学号'],
                            real_name=row['姓名'],
                            current_state=current_state,
                            phone_number=phone_number,
                            date=date,
                            id_number=id_number,
                            related_class=related_class,
                            tutor=tutor,
                            branch=branch,
                            application_date=application_date,
                        )
                        new_ccp_member.save()
                    except IntegrityError:
                        context = {
                            'error': '''已经有学号为"{}"的同学了'''.format(row['学号']),
                            'return_url': "user_info_manage",
                        }
                        return render(request, "main_site/error.html", context=context)
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


# 上传支部信息
@is_teacher
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
                        student_id_1=row['学号1'],
                        branch_secretary_1=row['组织委员'],
                        student_id_2=row['学号2'],
                        branch_secretary_2=row['宣传委员'],
                        student_id_3=row['学号3'],
                        tutor=row['对应导师'],
                        classes=row['对应班级'],
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


# 支部信息
@is_secretary
def branch_info(request):
    context = {}
    if request.method == "GET":
        try:
            current_ccp_member = CcpMember.objects.get(real_name=request.user.real_name, student_id=request.user.student_id)
            context['results'] = CcpMember.objects.filter(branch=current_ccp_member.branch)
        except ObjectDoesNotExist:
            context['results'] = None
        context['select'] = "manage"
        context['select_1'] = "branch_info"
        return render(request, "user_info/branch_member.html", context=context)


def valid(request):
    if request.method == "POST":
        # 用户名约束
        if request.POST['class_name'] == "username":
            if len(request.POST['value']) < 5:
                return HttpResponse("太短辣，至少五个字符哦")
            elif len(User.objects.filter(username=request.POST['value'])) != 0:
                return HttpResponse("已有此用户名")
            else:
                return HttpResponse("OK")
        # 密码约束
        elif request.POST['class_name'] == "password":
            if len(request.POST['value']) < 8:
                return HttpResponse("太短辣，至少八个字符哦")
            else:
                return HttpResponse("OK")

        elif request.POST['class_name'] == "real_name":
            if len(request.POST['value']) < 2:
                return HttpResponse("你的名字只有姓？")
            else:
                return HttpResponse("OK")

        elif request.POST['class_name'] == "student_id":
            if not request.POST['value'].isdigit() or len(request.POST['value']) != 10:
                return HttpResponse("学号必须是十位数字哦")
            elif len(User.objects.filter(student_id=request.POST['value'])) != 0:
                return HttpResponse("已有用户注册了此学号，请联系管理员！")
            else:
                return HttpResponse("OK")

        elif request.POST['class_name'] == "week_start":
            if request.POST['value'].isdigit():
                return HttpResponse("OK")
            else:
                return HttpResponse("不能为空")

        elif request.POST['class_name'] == "week_end":
            if request.POST['value'].isdigit():
                return HttpResponse("OK")
            else:
                return HttpResponse("不能为空")
        # 其他缺省的值
        else:
            if len(request.POST['value']) != 0:
                return HttpResponse("OK")
            else:
                return HttpResponse("不能为空")
