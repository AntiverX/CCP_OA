from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from .models import CourseInfo
from user_info.models import CcpMember
from django.db import transaction
from CCP.settings import BASE_DIR
import pandas as pd
from .models import DocumentInfo

def index(request):
    context = {}
    return render(request, "journey/index.html", context=context)


def course(request):
    context = {
        'select':"journey_course"
    }
    results = CourseInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)
    context['results'] = results
    return render(request, "journey/course.html", context=context)


def document(request):
    context = {
        'select':"journey_document"
    }
    results = DocumentInfo.objects.filter(student_id=request.user.student_id, real_name=request.user.real_name)
    context['results'] = results
    return render(request, "journey/document.html", context=context)


def course_manage(request):
    context = {
        'select':"manage"
    }
    if request.method == "GET":
        context['select'] = "manage"
        context['results'] = CourseInfo.objects.all()
        return render(request, "journey/course_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        if file is not None:
            with transaction.atomic():
                CourseInfo.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "user_info.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name)
                for index, row in data.iterrows():
                    new_CourseInfo = CourseInfo.objects.create(
                        student_id=row['学号'],
                        real_name=row['姓名'],
                        name=row['党课类型'],
                        date=row['时间'],
                        score=row['分数'],
                        auditor=row['审核人'],
                    )
                    new_CourseInfo.save()
                return HttpResponseRedirect("/journey/manage/course")
        else:
            new_CourseInfo = CcpMember.objects.create(
                student_id=request.POST['student_id'],
                real_name=request.POST['real_name'],
                branch=request.POST['branch'],
                current_state=request.POST['current_state'],
                phone_number=request.POST['phone_number'],
                date=request.POST['date'],
                sponsor=request.POST['sponsor'],
            )
            new_CourseInfo.save()
            return HttpResponseRedirect("/journey/manage/course")


def document_manage(request):
    context = {
        'select':"manage"
    }
    if request.method == "GET":
        context['select'] = "manage"
        context['results'] = DocumentInfo.objects.all()
        return render(request, "journey/document_manage.html", context=context)
    else:
        file = request.FILES.get('file')
        if file is not None:
            with transaction.atomic():
                DocumentInfo.objects.all().delete()
                file_name = BASE_DIR + "/static/cache/" + "user_info.xlsx"
                with open(file_name.encode(), "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                data = pd.read_excel(file_name)
                for index, row in data.iterrows():
                    new_DocumentInfo = DocumentInfo.objects.create(
                        student_id=row['学号'],
                        real_name=row['姓名'],
                        name=row['材料类型'],
                        date=row['时间'],
                        is_ok=row['通过'],
                        auditor=row['审核人'],
                    )
                    new_DocumentInfo.save()
                return HttpResponseRedirect("/journey/manage/document")
        else:
            new_DocumentInfo = DocumentInfo.objects.create(
                student_id=request.POST['student_id'],
                real_name=request.POST['real_name'],
                branch=request.POST['branch'],
                current_state=request.POST['current_state'],
                phone_number=request.POST['phone_number'],
                date=request.POST['date'],
                sponsor=request.POST['sponsor'],
            )
            new_DocumentInfo.save()
            return HttpResponseRedirect("/journey/manage/document")
