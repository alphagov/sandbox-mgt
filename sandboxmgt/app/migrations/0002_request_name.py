# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-12 11:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='name',
            field=models.TextField(null=True),
        ),
    ]
