# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-11 17:20
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20150613_1516'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='category',
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
