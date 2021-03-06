# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_webtest
from webtest import Upload
from users.models import User
from catalog.models import Category, Group
from tags.models import Tag
from documents.models import Document

import mock
from django.core.urlresolvers import reverse
import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.webtest]


@pytest.fixture(scope='function')
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture(scope='function')
def user():
    return User.objects.create_user(
        netid='nimarcha',
        email="lol@lol.be",
        first_name="Nikita",
        last_name="Marchant"
    )

@pytest.fixture(scope='function')
def tags():
    return [Tag.objects.create(name="my tag"), Tag.objects.create(name="my other tag")]


@pytest.fixture(scope='function')
def tree():
    root = Category.objects.create(name="ULB")
    science = Category.objects.create(name="science", parent=root)
    swag = Group.objects.create(name="Optimization of algorithmical SWAG", slug="swag-h-042")
    swag.categories.add(science)

    return root


def test_full_name_in_page(app, user):
    index = app.get('/', user=user.netid)
    assert user.name in index


def test_follow(app, user, tree):
    index = app.get('/', user=user.netid)
    catalog = index.click(href=reverse("show_groups"), index=0)
    category = catalog.click(description="science")
    group = category.click(description=lambda x: "Optimization" in x)
    group = group.click(
        # description="S'abonner",
        href=reverse('join_group', args=("swag-h-042",)),
    ).follow()

    assert "Se désabonner" in group

    index = app.get('/', user=user.netid)
    assert "swag-h-042" in index

    group = group.click(
        href=reverse('leave_group', args=("swag-h-042",)),
    ).follow()

    index = app.get('/', user=user.netid)
    assert "swag-h-042" not in index


def test_follow_from_category(app, user, tree):
    index = app.get('/', user=user.netid)
    catalog = index.click(href=reverse("show_groups"), index=0)
    category = catalog.click(description="science")
    category = category.click(description=lambda x: "swag-h-042" in x).follow()
    group = category.click(description=lambda x: x.startswith("Optimization"))
    assert "Se désabonner" in group


# @mock.patch.object(Document, 'add_to_queue')
@pytest.mark.slow
def test_simple_upload(app, user, tree, tags):
    group = app.get(reverse('group_show', args=("swag-h-042",)), user=user.netid)
    put = group.click(description="Uploader un fichier")
    form = put.forms[0]
    form['file'] = Upload('documents/tests/files/3pages.pdf')
    form['tags'].select_multiple(texts=['my tag'])
    response = form.submit()
    group = response.follow()

    assert Document.objects.count() == 1
    assert "3pages" in group
