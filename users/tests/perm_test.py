# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from users.models import User
from catalog.models import Category, Group
from documents.models import Document

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def tree():
    root = Category.objects.create(name="ULB")
    science = Category.objects.create(name="science", parent=root)

    swag = Group.objects.create(name="Optimization of algorithmical SWAG", slug="swag-h-042")
    swag.categories.add(science)

    yolo = Group.objects.create(name="Yolo as new life manager", slug="yolo-f-101")
    yolo.categories.add(science)

    return root


@pytest.fixture(scope='function')
def user():
    return User.objects.create_user(
        netid='myuser',
        email="myuser@lol.be",
        first_name="My",
        last_name="User"
    )


@pytest.fixture(scope='function')
def other_user():
    return User.objects.create_user(
        netid='otheruser',
        email="otheruser@lol.be",
        first_name="OtherU",
        last_name="ser"
    )


def test_superuser(user, other_user):
    user.is_staff = True
    user.save()
    doc = Document.objects.create(user=other_user)
    assert user.write_perm(doc)


def test_other_user(user, other_user):
    doc = Document.objects.create(user=user)
    assert not other_user.write_perm(doc)


def test_owner(user):
    doc = Document.objects.create(user=user)
    assert user.write_perm(doc)


def test_moderator(user, other_user, tree):
    group = Group.objects.last()
    user.moderated_groups.add(group)

    doc = Document.objects.create(user=other_user, group=group)
    assert user.write_perm(doc)


def test_bad_moderator(user, other_user, tree):
    group = Group.objects.last()
    other_group = Group.objects.first()
    assert group.id != other_group.id

    user.moderated_groups.add(group)

    doc = Document.objects.create(user=other_user, group=other_group)
    assert not user.write_perm(doc)


# TODO : do the same for threads and messages
