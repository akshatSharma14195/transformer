# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import URLMapper, URLAccessLogger
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from django.urls import reverse
import requests, json
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hola!")


def get_requests_func(request_method):
    request_method = request_method.lower()
    return {
        'post': requests.post,
        'put': requests.put,
        'delete': requests.delete,
        'patch': requests.patch,
    }[request_method]


def get_meta_header(key):
    return 'HTTP_' + key.replace('-', '_').upper()


@csrf_exempt
def transform(request, access_key):
    # check if access_key exists
    try:
        url_map = URLMapper.objects.get(access_key=access_key)

    except ObjectDoesNotExist:
        return HttpResponseBadRequest('<h1>Invalid access key</h1>')

    # need to get keyMaps
    new_request_obj = {}
    old_request_obj = request.GET
    old_request_obj.update(request.POST)
    try:
        for key_map in url_map.keymapper_set.all():
            if key_map.input_key in old_request_obj:
                new_request_obj[key_map.output_key] = old_request_obj[key_map.input_key]

    except EmptyResultSet:
        print "No keys to map"
        return HttpResponseBadRequest('<h1>Invalid transform</h1>')

    try:
        all_headers = url_map.headermapper_set.all()
    except EmptyResultSet:
        print "No keys to map"
        return HttpResponseBadRequest('<h1>No headers found</h1>')

    # need to initiate new_headers with headers of this request

    new_headers = {}
    for key_row in all_headers:
        print get_meta_header(key_row.header_key)
        new_headers[key_row.header_key] = request.META.get(get_meta_header(key_row.header_key)) or key_row.header_value

    if request.method == 'GET':
        response = requests.get(url_map.web_hook_url, headers=new_headers, params=new_request_obj,
                                cookies=request.COOKIES)
    else:
        req_func = get_requests_func(request.method)
        response = req_func(url_map.web_hook_url, headers=new_headers, data=new_request_obj,
                            cookies=request.COOKIES)

    # need to log here
    resp_data = response.text
    try:
        url_map.urlaccesslogger_set.create(input_data=old_request_obj, output_data=new_request_obj,
                                           response_data=resp_data)
    except Exception as e:
        # unsure what exception to handle here^
        print "Unexpected error on logging", e
    return HttpResponse(response)


@login_required
def viewlogs(request):
    user = request.user
    try:
        web_hooks = URLMapper.objects.filter(permissionmapper__group__user__id=user.id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Invalid user!")
    return render(request, 'transformer/log_view.html', {
        'user': user,
        'web_hook_url_list': web_hooks
    })


@login_required
def get_logs(request):
    try:
        urlAccessLogs = URLAccessLogger.objects.filter(url_mapper_id=request.POST.get('web_hook_id'))\
            .order_by('-created_at')
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Refresh page!")
    except KeyError:
        return HttpResponseBadRequest("Invalid parameters!")

    return JsonResponse({'log_rows': [{'id': x.id,
                                       'input_data': json.dumps(x.input_data, indent=2),
                                       'output_data': json.dumps(x.output_data,indent=2),
                                       'response_data': escape(x.response_data),
                                       'created_at': x.created_at.strftime('%Y-%m-%d %H:%M')
                                       } for x in urlAccessLogs]})


def get_login(request):
    if not request.user.is_authenticated:
        return render(request, 'transformer/login_view.html')
    else:
        return HttpResponseRedirect(reverse('transformer:view_logs'))


def login_submit(request):
    print request.POST
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
    except KeyError:
        return HttpResponseBadRequest("Enter username and password!")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('transformer:view_logs'))
    else:
        return HttpResponse("Invalid username or password!")
