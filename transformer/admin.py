# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.contrib import admin
from django.conf import settings
import json

from .models import URLMapper, KeyMapper, PermissionMapper, HeaderMapper, URLAccessLog
# Register your models here.


class KeyMapperInline(admin.TabularInline):
    model = KeyMapper


class HeaderMapperInline(admin.TabularInline):
    model = HeaderMapper


class PermissionMapperInline(admin.TabularInline):
    model = PermissionMapper


def get_access_url(obj):
    return settings.PREFIX_URL + reverse('transformer:map_url', kwargs={'access_key': obj.access_key})


get_access_url.short_description = 'Access URL'


class URLMapperAdmin(admin.ModelAdmin):
    list_display = ("title", "web_hook_url", get_access_url)
    inlines = [
        KeyMapperInline,
        HeaderMapperInline,
        PermissionMapperInline,
    ]


def get_created_at(obj):
    return obj.created_at.strftime('%Y-%m-%d %H:%M')


get_created_at.short_description = 'Created At'


def get_input_data(obj):
    return json.dumps(obj.input_data)


get_input_data.short_description = "Input Data"


def get_output_data(obj):
    return json.dumps(obj.output_data)


get_output_data.short_description = "Output Data"


class URLAccessLogAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "input_data", "output_data", "response_data")
    list_display = ("web_hook_url", "access_url", get_created_at,
                    get_input_data, get_output_data,
                    "response_data", "access_method")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super(URLAccessLogAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(URLMapper, URLMapperAdmin)
admin.site.register(URLAccessLog, URLAccessLogAdmin)
