from django.http import HttpResponseRedirect
from django.shortcuts import render

from activity.models import Activity


def index(request):
    context = {
        "select": "activity"
    }
    return render(request, "activity/index.html", context=context)


def manage(request):
    context = {}
    return render(request, "activity/manage.html", context=context)


def activityInfo(request):
    """"""
    context = {
        "select": "activity"
    }
    return render(request, "activity/index.html", context=context)


def joinActivity(request):
    """"""
    context = {
        "select": "activity"
    }
    return render(request, "activity/activity.html", context=context)


def activityAdd(request):
    """"""
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


def activityAll(request):
    """"""
    context = {
        "select": "activity",
        "activities": Activity.objects.all()
    }
    return render(request, "activity/manage.html", context=context)

