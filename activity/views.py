from django.shortcuts import render


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
