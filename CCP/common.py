from django.contrib.auth.decorators import REDIRECT_FIELD_NAME, user_passes_test
from django.shortcuts import HttpResponseRedirect, render


def teacher_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_teacher,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def is_secretary(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_gxh or request.user.is_teacher or request.user.is_secretary):
            return function(request, *args, **kwargs)
        else:
            context = {
                'error': "你无权访问此页面",
                'return_url': "manage",
            }
            return render(request, 'main_site/error.html', context=context)

    return wrap


def is_gxh(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_gxh or request.user.is_teacher):
            return function(request, *args, **kwargs)
        else:
            context = {
                'error': "你无权访问此页面",
                'return_url': "manage",
            }
            return render(request, 'main_site/error.html', context=context)

    return wrap


def is_teacher(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_teacher:
            return function(request, *args, **kwargs)
        else:
            context = {
                'error': "你无权访问此页面",
                'return_url': "manage",
            }
            return render(request, 'main_site/error.html', context=context)

    return wrap
