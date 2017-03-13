# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
import json
from os import path
from optparse import make_option
import yaml

from django.conf import settings
from catalog.models import Category, Group
from libulb.catalog.course import Course as ULBGroup


class Command(BaseCommand):
    help = 'Loads a new groups tree into the database'

    option_list = BaseCommand.option_list + (
        make_option(
            '--hit-ulb',
            action='store_true',
            dest='hitulb',
            default=False,
            help='Hit ULB servers to get groups names from slugs'
        ),
        make_option(
            '--tree',
            dest='tree_file',
            help='Path to the .yaml tree file'
        ),
    )
    
    LOCAL_CACHE = {}
    YEAR = "201617"

    def handle(self, *args, **options):
        self.stdout.write('Loading tree ... ')

        if not options['hitulb']:
            f = path.join(settings.BASE_DIR, 'catalog/management/localcache.json')
            self.LOCAL_CACHE = json.loads(open(f).read())

        tree = yaml.load(open(options['tree_file']))

        Category.objects.all().delete()

        root = Category.objects.create(
            name="Groupes",
            slug="root",
            parent=None,
        )
        
        
        catCoursULB = Category.objects.create(
            name="Cours ULB",
            slug="",
            parent=root
        )
        
        catGroupesPublics = Category.objects.create(
            name="Groupes Publics",
            slug="",
            parent=root
        )
        
        for catName in ("Cercles", "Facultés", "Etudiants"):
            cat = Category.objects.create(
                name=catName,
                slug="",
                parent=catGroupesPublics
            )
        

        self.create_tree(catCoursULB, tree)

        self.stdout.write('Done \n')

    def create_tree(self, father, tree):
        if isinstance(tree, dict):
            for key, value in tree.items():
                cat = Category.objects.create(
                    name=key,
                    slug="",
                    parent=father
                )
                self.create_tree(cat, value)

        if isinstance(tree, str):
            try:
                group = Group.objects.get(slug=tree)
            except Group.DoesNotExist:
                if self.LOCAL_CACHE:
                    name = self.LOCAL_CACHE.get(tree, "Unknown group in cache")
                else:
                    ulb_group = ULBGroup.get_from_slug(tree, self.YEAR)
                    name = ulb_group.name
                group = Group.objects.create(name=name, slug=tree, type="C")
            group.categories.add(father)

        if isinstance(tree, list):
            for subtree in tree:
                self.create_tree(father, subtree)
