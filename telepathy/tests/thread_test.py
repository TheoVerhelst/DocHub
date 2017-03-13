# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from telepathy.models import Thread
from users.models import User
from catalog.models import Group
import json

pytestmark = pytest.mark.django_db


def create_thread(name):
    group = Group.objects.create(slug='AAA-000')
    user = User.objects.create_user(netid='test_user')
    thread = Thread.objects.create(name=name, user=user, group=group)

    return thread


def test_page_number_is_none():
    thread = create_thread('coucou')
    assert thread.page_no is None


def test_page_number():
    thread = create_thread('coucou')
    thread.placement = json.dumps({'page-no': 100})
    assert thread.page_no is 100
