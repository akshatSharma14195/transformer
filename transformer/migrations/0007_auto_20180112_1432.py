# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-12 09:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('transformer', '0006_auto_20180111_2009'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='permissionmapper',
            unique_together=set([('url_mapper', 'group')]),
        ),
    ]