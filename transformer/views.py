# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import URLMapper, URLAccessLogger
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.core.exceptions import ObjectDoesNotExist
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
        # need to get keyMaps
        try:
            new_request_obj = {}
            old_request_obj = request.GET
            old_request_obj.update(request.POST)
            for key_map in url_map.keymapper_set.all():
                if key_map.input_key in old_request_obj:
                    new_request_obj[key_map.output_key] = old_request_obj[key_map.input_key]

            # need to initiate new_headers with headers of this request?
            # Facing issue passing CSRF token to next request
            # new_headers = request.META
            new_headers = {}
            new_headers.update(url_map.extra_headers)

            print type(new_headers)
            if request.method == 'GET':
                response = requests.get(url_map.web_hook_url, headers=new_headers, params=new_request_obj, cookies=request.COOKIES)
            else:
                req_func = get_requests_func(request.method)
                response = req_func(url_map.web_hook_url, headers=new_headers, data=new_request_obj, cookies=request.COOKIES)

            # need to log here
            try:
                try:
                    resp_data = response.json()
                except Exception as e:
                    resp_data = {}
                    print "Could not resolve json", e, str(response)
                url_map.urlaccesslogger_set.create(input_data=old_request_obj, output_data=new_request_obj, response_data=resp_data)
            except Exception as e:
                print "Unexpected error on logging", e
            return HttpResponse(response)
        except Exception as e:
            print "Unexpected Error", e
            return HttpResponseServerError(e)

    except ObjectDoesNotExist:
        return HttpResponseBadRequest('<h1>Invalid access key</h1>')

    except Exception as e:
        print "Unexpected Error", e
        HttpResponseServerError(e)

