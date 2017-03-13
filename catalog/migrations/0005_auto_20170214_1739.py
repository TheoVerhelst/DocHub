# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-14 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_group_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='type',
            field=models.CharField(choices=[('C', 'Cours'), ('P', 'Public'), ('R', 'Privé')], default='P', max_length=1),
        ),
    ]
