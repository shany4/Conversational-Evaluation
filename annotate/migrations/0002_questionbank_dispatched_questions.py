# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-07 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionbank',
            name='dispatched_questions',
            field=models.TextField(default=b''),
        ),
    ]
