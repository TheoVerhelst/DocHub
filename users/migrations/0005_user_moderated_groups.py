# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20150613_1516'),
        ('users', '0004_remove_user_followed_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='moderated_groups',
            field=models.ManyToManyField(to='catalog.Group'),
            preserve_default=True,
        ),
    ]
