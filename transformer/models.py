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
    access_url = models.CharField(max_length=200, default=uuid.uuid4, editable=False)
    web_hook_url = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=250)
    allowed_headers = JSONField(default=json_default)

    def __str__(self):
        return str(self.access_url) + " -> " + self.web_hook_url


class KeyMapper(models.Model):
    input_key = models.CharField(max_length=100)
    output_key = models.CharField(max_length=100)
    corresponding_url_map = models.ForeignKey(URLMapper, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("input_key", "output_key", "corresponding_url_map")


class URLAccessLogger(models.Model):
    url_mapper_id = models.ForeignKey(URLMapper)
    input_data = JSONField(default=json_default)
    output_data = JSONField(default=json_default)
    response_data = JSONField(default=json_default)


class PermissionMapper(models.Model):
    url_mapper_id = models.ForeignKey(URLMapper)
    group_id = models.ForeignKey(Group)
