# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import URLMapper, URLAccessLogger
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet
import requests
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hola!")


def get_requests_func(request_method):
    request_method = request_method.lower()
    return {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
        'head': requests.head,
        'delete': requests.delete,
        'patch': requests.patch,
    }[request_method]


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

    # need to initiate new_headers with headers of this request?
    # Facing issue passing CSRF token to next request
    # new_headers = request.META
    new_headers = {}
    new_headers.update(url_map.extra_headers)

    if request.method == 'GET':
        response = requests.get(url_map.web_hook_url, headers=new_headers, params=new_request_obj,
                                cookies=request.COOKIES)
    else:
        req_func = get_requests_func(request.method)
        response = req_func(url_map.web_hook_url, headers=new_headers, data=new_request_obj,
                            cookies=request.COOKIES)

    # need to log here
    print type(response.text)
    resp_data = response.text
    try:
        url_map.urlaccesslogger_set.create(input_data=old_request_obj, output_data=new_request_obj,
                                           response_data=resp_data)
    except Exception as e:
        # unsure what exception to handle here^
        print "Unexpected error on logging", e
    return HttpResponse(response)


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


def get_logs(request):
    try:
        urlAccessLogs = URLAccessLogger.objects.filter(url_mapper_id=request.POST.get('web_hook_id'))\
            .order_by('-created_at')
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Refresh page!")
    except KeyError:
        return HttpResponseBadRequest("Invalid parameters!")

    return JsonResponse({'log_rows': [{'id': x.id,
                                       'input_data': str(x.input_data),
                                       'output_data': str(x.output_data),
                                       'response_data': x.response_data,
                                       'created_at': str(x.created_at)
                                       } for x in urlAccessLogs]})
