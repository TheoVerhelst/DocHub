# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(default='', blank=True),
            preserve_default=True,
        ),
    ]
