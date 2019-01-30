# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# Create your views here.
@login_required
def account(request):
    context = {}
    if request.POST.get('change_password') is not None:
        new_password = request.POST.get('new_password')

        user = User.objects.get(username=request.user.username)
        user.set_password(new_password)
        user.save()
        context['message'] = 'Password successfully changed.'
    return render(request, 'accounts.html', context)


@login_required
def get_accounts_management(request):
    """Super admin creates user, deactivates user, reactivates user"""
    context = {}
    all_users = [u for u in User.objects.all() if not u.is_superuser]
    active_users = [u for u in all_users if u.is_active]
    inactive_users = [u for u in all_users if not u.is_active]
    context['active_users'] = active_users
    context['inactive_users'] = inactive_users

    if request.POST.get('log_out') is not None:
        logout(request)
        context['message'] = 'Successfully logged out.'
        return render(request, 'log_in.html', context)

    if request.POST.get('create_new_user') is not None:
        # Check user name availability.
        # staff = False
        new_user_name = request.POST.get('new_user_name')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        staff = request.POST.get('staff')

        if len(User.objects.filter(username=new_user_name)) > 0:
            context['message'] = 'User name ' + new_user_name + ' is not available.'
            return render(request, 'accounts_management.html', context)

        staff_radio = False
        if staff == 'True':
            staff_radio = True

        new_user = User.objects.create_user(new_user_name, password=password, first_name=first_name, last_name=last_name)
        new_user.is_staff = staff_radio
        new_user.save()

    if request.POST.get('deactivate_user') is not None:
        message = 'User(s): '
        for u in active_users:
            if request.POST.get(u.username) is not None:
                print(u.is_staff)
                u.is_active = False
                u.save()
                message += u.username + ' '
        message += 'are now inactive.'
        context['message'] = message

    if request.POST.get('delete_user') is not None:
        for u in active_users:
            if request.POST.get(u.username) is not None:
                u.delete()

    if request.POST.get('reactivate_user') is not None:
        message = 'User(s): '
        for u in inactive_users:
            if request.POST.get(u.username) is not None:
                u.is_active = True
                u.save()
                message += u.username + ' '
        message += 'are now active.'
        context['message'] = message

    all_users = [u for u in User.objects.all() if not u.is_superuser]
    active_users = [u for u in all_users if u.is_active]
    inactive_users = [u for u in all_users if not u.is_active]
    context['active_users'] = active_users
    context['inactive_users'] = inactive_users

    return render(request, 'accounts_management.html', context)


@login_required
def get_home(request):
    if request.user.is_superuser:
        return get_accounts_management(request)
    return render(request, 'home.html')


def get_login(request):
    """Log in. Reset password."""
    context = {}
    if request.user.is_authenticated():
        if request.POST.get('log_out') is not None:
            return get_logout(request)
        return redirect('/accounts/home')

    if request.POST.get('log_in') is not None:
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')

        user = authenticate(username=user_name, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return get_login(request)
            else:
                context['message'] = 'Account has been disabled.'
        else:
            context['message'] = 'Invalid log in.'

    return render(request, 'log_in.html', context)


def get_logout(request):
    context = {}
    logout(request)
    context['message'] = 'Successfully logged out.'
    return render(request, 'log_in.html', context)

