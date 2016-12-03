# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from mptt.models import MPTTModel, TreeForeignKey


@python_2_unicode_compatible
class Category(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True)
    description = models.TextField(blank=True, default='')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['id']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Group(models.Model):
    GROUP_TYPES= (
        ("C", "Course"),
        ("P", "Public"),
        ("R", "Private"),
    )
    type = models.CharField(max_length=1, choices=GROUP_TYPES)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    categories = models.ManyToManyField(Category)

    class Meta:
        ordering = ['slug']

    def isCourse(self):
        return self.type == "C"

    def isPublic(self):
        return self.type == "P"
        
    def isPrivate(self):
        return self.type == "R"

    def gehol_url(self):
        if self.isCourse():
            slug = self.slug.replace('-', '').upper()
            return "http://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours=%s" % (slug,)
        else:
            return None

    def get_absolute_url(self):
        return reverse('group_show', args=(self.slug, ))

    def __str__(self):
        return self.slug.upper()

    def fullname(self):
        return "{} ({})".format(self.name, self.slug.lower())
