# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-10 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transformer', '0003_urlaccesslogger_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlaccesslogger',
            name='response_data',
            field=models.TextField(default=''),
        ),
    ]
