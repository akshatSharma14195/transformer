# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import Group
# Create your models here.


def json_default():
    return {}


class URLMapper(models.Model):
    access_key = models.UUIDField(default=uuid.uuid4, editable=False)
    web_hook_url = models.URLField(unique=True)
    title = models.CharField(max_length=250)

    def __str__(self):
        return str(self.access_key) + " -> " + self.web_hook_url


class KeyMapper(models.Model):
    input_key = models.CharField(max_length=100)
    output_key = models.CharField(max_length=100)
    corresponding_url_map = models.ForeignKey(URLMapper, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("input_key", "output_key", "corresponding_url_map")


class URLAccessLogger(models.Model):
    url_mapper = models.ForeignKey(URLMapper)
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
