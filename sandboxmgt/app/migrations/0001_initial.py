# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-22 18:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=255, null=True)),
                ('github', models.CharField(max_length=255, null=True)),
                ('message', models.TextField()),
                ('agree', models.BooleanField()),
            ],
        ),
    ]
