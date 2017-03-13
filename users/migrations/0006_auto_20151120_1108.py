# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_moderated_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='moderated_groups',
            field=models.ManyToManyField(to='catalog.Group', blank=True),
            preserve_default=True,
        ),
    ]
