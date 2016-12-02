# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from rest_framework import serializers

from catalog.models import Group, Category
from documents.serializers import DocumentSerializer
from telepathy.serializers import SmallThreadSerializer


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    document_set = DocumentSerializer(many=True)
    thread_set = SmallThreadSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            'id', 'name', 'slug', 'url',
            'categories', 'document_set', 'thread_set'
        )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ShortGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'url', 'slug', 'name', )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'slug', 'name', 'parent', 'children', 'group_set')

        extra_kwargs = {
            'group_set': {'lookup_field': 'slug'},
        }


class ShortCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'slug', 'name', )
