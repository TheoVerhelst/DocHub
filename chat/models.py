# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from catalog.models import Group
from django.conf import settings


@python_2_unicode_compatible
class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="chat_message_set")
    group = models.ForeignKey(Group, db_index=True, related_name="chat_message_set")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    def fullname(self):
        return "un message"
        return Truncator(self.__unicode__()).words(9)

    class Meta:
        ordering = ['-created']
