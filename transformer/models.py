# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid, json, requests
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse
# Create your models here.


def json_default():
    return {}


def get_meta_header(key):
    return 'HTTP_' + key.replace('-', '_').upper()


class URLMapper(models.Model):
    access_key = models.UUIDField(default=uuid.uuid4, editable=False)
    web_hook_url = models.URLField(unique=True)
    title = models.CharField(max_length=250)

    def transform_keys(self):
        old_request_data = self.old_request_data
        new_request_data = {}
        for key_map in self.keymapper_set.all():
            if key_map.input_key in old_request_data:
                new_request_data[key_map.output_key] = old_request_data[key_map.input_key]
        self.new_request_data = new_request_data
        return new_request_data

    def check_valid_request(self, request):
        content_type = request.META.get('CONTENT_TYPE')
        old_request_data = None
        if request.method == 'GET':
            old_request_data = request.GET.dict()
            self.request_type = 'GET'
        elif request.method == 'POST' and content_type == 'application/json':
            old_request_data = json.loads(request.body)
            self.request_type = 'POST_JSON'
        elif request.method == 'POST' and content_type == 'application/x-www-form-urlencoded':
            old_request_data = request.POST.dict()
            self.request_type = 'POST_FORM'
        self.old_request_data = old_request_data
        self.old_headers = request.META
        self.cookies = request.COOKIES
        if not old_request_data:
            raise ValueError('Invalid request type')

    def set_headers(self):
        old_headers = self.old_headers
        new_headers = {
            'Content-type': old_headers.get('CONTENT_TYPE')
        }
        old_headers_to_log = {
            'CONTENT_TYPE': old_headers.get('CONTENT_TYPE')
        }
        for header_map in self.headermapper_set.all():
            curr_key = get_meta_header(header_map.header_key)
            new_headers[header_map.header_key] = \
                old_headers.get(curr_key, header_map.header_value)
            old_headers_to_log[curr_key] = old_headers.get(curr_key, "")
        self.new_headers = new_headers
        self.old_headers_to_log = old_headers_to_log

    def get_access_url(self):
        return '{}{}'.format(settings.PREFIX_URL, reverse('transformer:map_url',
                                                          kwargs={'access_key': self.access_key}))

    def get_response(self):
        response = None
        if self.request_type == 'GET':
            response = requests.get(self.web_hook_url, headers=self.new_headers,
                                    params=self.new_request_data, cookies=self.cookies)
        elif self.request_type == 'POST_JSON':
            response = requests.post(self.web_hook_url, headers=self.new_headers,
                                     json=self.new_request_data, cookies=self.cookies)
        elif self.request_type == 'POST_FORM':
            response = requests.post(self.web_hook_url, headers=self.new_headers,
                                     data=self.new_request_data, cookies=self.cookies)
        self.response = response
        return response

    def __str__(self):
        return '{} -> {}'.format(unicode(self.get_access_url()), self.web_hook_url)

    def log_transform(self):
        URLAccessLog.objects.create(input_data=self.old_request_data,
                                    access_url=self.get_access_url(),
                                    web_hook_url=self.web_hook_url,
                                    access_method=self.request_type,
                                    old_headers=self.old_headers_to_log,
                                    new_headers=self.new_headers,
                                    output_data=json.dumps(self.new_request_data),
                                    response_data=str(self.response.__dict__))


class KeyMapper(models.Model):
    input_key = models.CharField(max_length=100)
    output_key = models.CharField(max_length=100)
    corresponding_url_map = models.ForeignKey(URLMapper, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("input_key", "output_key", "corresponding_url_map")


class URLAccessLog(models.Model):
    access_url = models.URLField()
    web_hook_url = models.URLField()
    access_method = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    input_data = JSONField(default=json_default)
    output_data = models.TextField(default='')
    old_headers = JSONField(default=json_default)
    new_headers = JSONField(default=json_default)
    response_data = models.TextField(default='')


class PermissionMapper(models.Model):
    url_mapper = models.ForeignKey(URLMapper)
    group = models.ForeignKey(Group)

    class Meta:
        unique_together = ("url_mapper", "group")


class HeaderMapper(models.Model):
    header_key = models.CharField(max_length=100)
    header_value = models.CharField(max_length=100)
    url_mapper = models.ForeignKey(URLMapper)
