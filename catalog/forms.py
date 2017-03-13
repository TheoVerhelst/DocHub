# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm, RadioSelect
from catalog.models import Group

class NewGroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'slug', 'type', 'categories']
        widgets = {
            'type' : RadioSelect()
        }
        labels = {
            'type': 'Type',
            'name': 'Nom',
            'slug': 'Slug',
            'categories' : 'Catégorie(s)'
        }
        help_texts = {
            'type': 'Type du groupe',
            'name': 'Nom du groupe',
            'slug': 'Le slug et une version condensée du nom. Ex: pour le groupe "Cercle Informatique", le slug pourrait être "CI".',
            'categories' : 'Catégories auquelles ce groupe appartient'
        }

