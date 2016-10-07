# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import os
from os.path import join

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone
from django.conf import settings
import actstream
import users.identicon
import libnetid

from catalog.models import Course


class CustomUserManager(libnetid.django.models.LibNetidUserManager):
    PATTERN = re.compile('[\W_]+')

    def _create_user(self, *args, **kwargs):
        user = super()._create_user(*args, **kwargs)
        if settings.IDENTICON:
            IDENTICON_SIZE = 120
            if not os.path.exists(join(settings.MEDIA_ROOT, "profile")):
                os.makedirs(join(settings.MEDIA_ROOT, "profile"))
            profile_path = join(settings.MEDIA_ROOT, "profile", "{}.png".format(user.netid))
            alpha_netid = self.PATTERN.sub('', user.netid)
            users.identicon.render_identicon(int(alpha_netid, 36), IDENTICON_SIZE / 3).save(profile_path)
            user.photo = 'png'
        user.save(using=self._db)
        return user


class User(libnetid.django.models.AbstractNetidUser):

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = join(settings.STATIC_URL, "images/default.jpg")
    objects = CustomUserManager()

    edited = models.DateTimeField(auto_now=True)
    photo = models.CharField(max_length=10, default="")
    welcome = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default='')

    is_academic = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)

    moderated_courses = models.ManyToManyField('catalog.Course', blank=True)

    notify_on_response = models.BooleanField(default=True)
    notify_on_new_doc = models.BooleanField(default=True)
    notify_on_new_thread = models.BooleanField(default=True)
    notify_on_mention = True
    notify_on_upload = True

    def __init__(self, *args, **kwargs):
        self._following_courses = None
        self._moderated_courses = None
        super(User, self).__init__(*args, **kwargs)

    @property
    def get_photo(self):
        photo = self.DEFAULT_PHOTO
        if self.photo != "":
            photo = join(settings.MEDIA_URL, "profile/{0.netid}.{0.photo}".format(self))

        return photo

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)

    def notification_count(self):
        return self.notification_set.filter(read=False).count()

    def following(self):
        return actstream.models.following(self)

    def following_courses(self):
        if self._following_courses is None:
            self._following_courses = actstream.models.following(self, Course)
        return self._following_courses

    def has_module_perms(self, *args, **kwargs):
        return True # TODO : is this a good idea ?

    def has_perm(self, perm_list, obj=None):
        return self.is_staff

    def write_perm(self, obj):
        if self.is_staff:
            return True

        if obj is None:
            return False

        if self._moderated_courses is None:
            ids = [course.id for course in self.moderated_courses.only('id')]
            self._moderated_courses = ids

        return obj.write_perm(self, self._moderated_courses)

    def fullname(self):
        return self.get_full_name()


class Inscription(libnetid.django.models.AbstractInscription):
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
