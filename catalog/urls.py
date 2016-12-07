# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from catalog.views import CategoryDetailView, GroupDetailView
import catalog.views

urlpatterns = [
    url(r"^group/(?P<slug>[^/]*)$", GroupDetailView.as_view(), name="group_show"),
    url(r"^category/(?P<pk>\d+)$", CategoryDetailView.as_view(), name="category_show"),

    url(r"^join/(?P<slug>[^/]*)$", catalog.views.join_group, name="join_group"),
    url(r"^leave/(?P<slug>[^/]*)$", catalog.views.leave_group, name="leave_group"),
    url(r"^my_groups/$", catalog.views.show_my_groups, name="show_my_groups"),
    url(r"^all_groups/$", catalog.views.show_all_groups, name="show_all_groups"),

    url(r"^group_tree.json$", catalog.views.group_tree, name="group_tree"),
]
