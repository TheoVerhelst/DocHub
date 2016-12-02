# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.core.management import call_command
from catalog.models import Group, Category
from django.conf import settings

import pytest


pytestmark = [pytest.mark.django_db]

fixtures = os.path.join(settings.BASE_DIR, 'catalog', 'tests', 'fixtures')
SIMPLE_TREE = os.path.join(fixtures, 'simple_tree.yaml')
MULTIPLE_TREE = os.path.join(fixtures, 'multiple_tree.yaml')
REAL_TREE = os.path.join(fixtures, 'real_tree.yaml')


def test_load_tree():
    call_command('loadtree', tree_file=SIMPLE_TREE)

    ulb = Category.objects.get(level=0)
    assert ulb.name == "ULB"

    opti = Group.objects.get(slug="opti-f-1001")
    assert opti.categories.count() == 1
    options = opti.categories.last()

    assert options.name == "Options"
    assert options.level == 3


def test_load_multiple_tree():
    call_command('loadtree', tree_file=MULTIPLE_TREE)

    info = Category.objects.get(name="Informatique")
    assert info.level == 1

    phys = Category.objects.get(name="Physique")
    assert phys.level == 1

    master = phys.children.first()
    assert master.name == "Master"
    assert master.group_set.count() == 1
    assert master.group_set.last().slug == "phys-h-200"


def test_empty_tree():
    category = Category.objects.create(name="Caca", slug="prout")
    group = Group.objects.create(name="Testing", slug="test-h-100")

    group.categories.add(category)

    call_command('loadtree', tree_file=SIMPLE_TREE)

    assert Category.objects.filter(slug="prout").count() == 0

    group = Group.objects.get(slug="test-h-100")
    assert group.categories.count() == 0


def test_fill_twice():
    call_command('loadtree', tree_file=SIMPLE_TREE)

    group = Group.objects.last()
    group.name = "Autre chose"
    group.save()

    call_command('loadtree', tree_file=SIMPLE_TREE)

    new_group = Group.objects.get(slug=group.slug)
    assert new_group.id == group.id
    assert group.name == new_group.name


@pytest.mark.slow
@pytest.mark.network
def test_load_tree_hit_ulb():
    call_command('loadtree', hitulb=True, tree_file=REAL_TREE)

    info = Group.objects.get(slug="info-f-101")
    assert info.name == "Programmation"
