# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-10 06:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('transformer', '0002_auto_20180109_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlaccesslogger',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]