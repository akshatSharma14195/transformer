# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-08 13:40
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import transformer.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyMapper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_key', models.CharField(max_length=100)),
                ('output_key', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionMapper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='URLAccessLogger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', django.contrib.postgres.fields.jsonb.JSONField(default=transformer.models.json_default)),
                ('output_data', django.contrib.postgres.fields.jsonb.JSONField(default=transformer.models.json_default)),
                ('response_data', django.contrib.postgres.fields.jsonb.JSONField(default=transformer.models.json_default)),
            ],
        ),
        migrations.CreateModel(
            name='URLMapper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_url', models.CharField(default=uuid.uuid4, editable=False, max_length=200)),
                ('web_hook_url', models.CharField(max_length=200, unique=True)),
                ('title', models.CharField(max_length=250)),
                ('allowed_headers', django.contrib.postgres.fields.jsonb.JSONField(default=transformer.models.json_default)),
            ],
        ),
        migrations.AddField(
            model_name='urlaccesslogger',
            name='url_mapper_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transformer.URLMapper'),
        ),
        migrations.AddField(
            model_name='permissionmapper',
            name='url_mapper_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transformer.URLMapper'),
        ),
        migrations.AddField(
            model_name='keymapper',
            name='corresponding_url_map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transformer.URLMapper'),
        ),
        migrations.AlterUniqueTogether(
            name='keymapper',
            unique_together=set([('input_key', 'output_key', 'corresponding_url_map')]),
        ),
    ]