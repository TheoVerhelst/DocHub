# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from functools import partial

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from mptt.utils import get_cached_trees

from actstream import actions
import actstream

from catalog.models import Category, Group
from catalog.suggestions import suggest
from telepathy.forms import NewThreadForm, MessageForm


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "catalog/category.html"
    context_object_name = "category"


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = "catalog/group.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        group = context['group']

        context['documents'] = group.document_set\
            .exclude(state="ERROR", hidden=True)\
            .select_related('user')\
            .prefetch_related('tags')
        context['threads'] = group.thread_set.annotate(Count('message'))\
                .prefetch_related('message_set')
        context['thread_form'] = NewThreadForm()
        context['form'] = MessageForm()
        context['followers_count'] = len(actstream.models.followers(group))

        return context


def set_follow_group(request, slug, action):
    group = get_object_or_404(Group, slug=slug)
    action(request.user, group)
    nextpage = request.GET.get('next', reverse('group_show', args=[slug]))
    return HttpResponseRedirect(nextpage)


@login_required
def join_group(request, slug):
    follow = partial(actions.follow, actor_only=False)
    return set_follow_group(request, slug, follow)


@login_required
def leave_group(request, slug):
    return set_follow_group(request, slug, actions.unfollow)


@login_required
def show_my_groups(request):
    return render(request, "catalog/my_groups.html", {
        "groups" : request.user.following_groups(),
        "suggestions": suggest(request.user)
    })

@login_required
def show_all_groups(request):
    return render(request, "catalog/all_groups.html", {
        "categories" : Category.objects.prefetch_related('group_set').all()
    })


@cache_page(60 * 60)
@login_required
def group_tree(request):
    def group(node):
        return {
            'name': node.name,
            'id': node.id,
            'slug': node.slug,
        }

    def category(node):
        return {
            'name': node.name,
            'id': node.id,
            'children': list(map(category, node.get_children())),
            'groups': list(map(group, node.group_set.all())),
        }

    categories = list(map(category, get_cached_trees(Category.objects.all())))
    return HttpResponse(json.dumps(categories),
                        content_type="application/json")
