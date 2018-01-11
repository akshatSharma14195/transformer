# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
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

    def get_transformed_keys(self, old_request_obj):
        new_request_obj = {}
        for key_map in self.keymapper_set.all():
            if key_map.input_key in old_request_obj:
                new_request_obj[key_map.output_key] = old_request_obj[key_map.input_key]
        return new_request_obj

    def get_headers(self, old_header):
        new_headers = {}
        for key_row in self.headermapper_set.all():
            new_headers[key_row.header_key] = \
                old_header.get(get_meta_header(key_row.header_key)) \
                or key_row.header_value
        return new_headers

    def make_log(self, input_data, output_data, response_data):
        self.urlaccesslogger_set.create(input_data=input_data,
                                        output_data=output_data,
                                        response_data=response_data)

    def get_access_url(self):
        return settings.PREFIX_URL + reverse('transformer:map_url',
                                             kwargs={'access_key': self.access_key})

    def __str__(self):
        return str(self.access_key) + " -> " + self.web_hook_url


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
    output_data = JSONField(default=json_default)
    response_data = models.TextField(default='')


class PermissionMapper(models.Model):
    url_mapper = models.ForeignKey(URLMapper)
    group = models.ForeignKey(Group)


class HeaderMapper(models.Model):
    header_key = models.CharField(max_length=100)
    header_value = models.CharField(max_length=100)
    url_mapper = models.ForeignKey(URLMapper)
