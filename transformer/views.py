# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import URLMapper, URLAccessLog
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.urls import reverse
import json
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hola!")

@csrf_exempt
def transform(request, access_key):
    # check if access_key exists
    try:
        url_map = URLMapper.objects.get(access_key=access_key)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest('<h1>Invalid access key</h1>')

    try:
        url_map.check_valid_request(request)
        url_map.transform_keys()
        url_map.set_headers()
    except ValueError as e:
        print e
        return HttpResponseBadRequest('<h1>Invalid request type</h1>')

    response = url_map.get_response()
    url_map.log_transform()

    return HttpResponse(response)


@login_required
def view_logs(request):
    user = request.user
    try:
        access_urls = URLMapper.objects.filter(permissionmapper__group__user=user)
    except URLMapper.DoesNotExist:
        return HttpResponseBadRequest("Invalid user!")
    return render(request, 'transformer/log_view.html', {
        'user': user,
        'access_url_list': [{'access_url': x.get_access_url()} for x in access_urls]
    })


@login_required
def get_logs(request):
    try:
        url_access_logs = URLAccessLog.objects.filter(access_url=request.POST.get('access_url'))\
            .order_by('-created_at')
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Refresh page!")
    except KeyError:
        return HttpResponseBadRequest("Invalid parameters!")

    return JsonResponse({'log_rows': [{'id': x.id,
                                       'web_hook_url': x.web_hook_url,
                                       'input_data': json.dumps(x.input_data, indent=2),
                                       'output_data': x.output_data,
                                       'old_headers': json.dumps(x.old_headers, indent=2),
                                       'new_headers': json.dumps(x.new_headers, indent=2),
                                       'response_data': escape(x.response_data),
                                       'access_type': x.access_method,
                                       'created_at': x.created_at.strftime('%Y-%m-%d %H:%M')
                                       } for x in url_access_logs]})


def get_login(request):
    if not request.user.is_authenticated:
        return render(request, 'transformer/login_view.html')
    else:
        return HttpResponseRedirect(reverse('transformer:view_logs'))


def login_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('transformer:view_logs'))
    else:
        return HttpResponse("Invalid username or password!")


def logout_view(request):
    return logout(request)
