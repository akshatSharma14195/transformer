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
import requests, json
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

    # need to get keyMaps
    old_request_obj = request.GET.dict()
    old_request_obj.update(request.POST.dict())
    old_request_obj.update(json.loads(request.body))
    new_request_obj = url_map.get_transformed_keys(old_request_obj)
    new_headers = url_map.get_headers(request.META)

    # need to initiate new_headers with headers of this request

    if request.method == 'GET':
        response = requests.get(url_map.web_hook_url, headers=new_headers,
                                params=new_request_obj, cookies=request.COOKIES)
    else:
        response = requests.post(url_map.web_hook_url, headers=new_headers,
                                 data=new_request_obj, cookies=request.COOKIES)

    # need to log here
    URLAccessLog.objects.create(input_data=old_request_obj,
                                access_url=url_map.get_access_url(),
                                web_hook_url=url_map.web_hook_url,
                                access_method=request.method,
                                output_data=new_request_obj,
                                response_data=str(response.__dict__))

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
                                       'output_data': json.dumps(x.output_data,indent=2),
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
