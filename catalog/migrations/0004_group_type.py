# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-03 14:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_remove_group_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='type',
            field=models.CharField(choices=[('C', 'Course'), ('P', 'Public'), ('R', 'Private')], default='C', max_length=1),
            preserve_default=False,
        ),
    ]
