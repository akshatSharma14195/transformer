# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import URLMapper, KeyMapper, PermissionMapper
# Register your models here.
admin.site.register(URLMapper)
admin.site.register(KeyMapper)
admin.site.register(PermissionMapper)
