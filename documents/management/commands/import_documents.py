# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import glob
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.files import File

from users.models import User
from catalog.models import Group
from documents import logic

TAGS = {
    'off': 'officiel',
    'ref': 'référence',
    'sli': 'slides',
    'res': 'résumé',
    'exa': 'examen',
    'tp': 'tp',
    'syl': 'syllabus',
    'cor': 'corrigé',
    'corr': 'corrigé',
    'for': 'formulaire',
    'sol': 'corrigé',
    'lab': 'laboratoire',
    'law': 'loi',
}


class Command(BaseCommand):

    help = 'Import documents in a group'
    option_list = BaseCommand.option_list + (
        make_option('--path', action='store', dest='path', default='', help='Documents path'),
        make_option('--user', action='store', dest='username', default='', help='user owning the documents'),
        make_option('--group', action='store', dest='group_slug', default='', help='group slug'),
    )

    def handle(self, *args, **options):
        netid = options["username"]
        self.stdout.write('Looking for user "{}"'.format(netid))

        user = User.objects.filter(netid=netid).first()
        if user is None:
            self.stdout.write('Could not find user.')
            return

        slug = options["group_slug"]
        self.stdout.write('Looking for group "{}"'.format(slug))

        group = Group.objects.filter(slug=slug).first()
        if group is None:
            self.stdout.write('Could not find group.')
            return

        path = options['path']
        self.stdout.write('Gathering documents in "{}"'.format(path))
        if not os.path.exists(path):
            self.stdout.write("Path does not exist")
            return

        paths = glob.glob(os.path.join(path, "*.*"))

        for doc_path in paths:
            import_document_from_path(doc_path, group, user)
            self.stdout.write('.', ending='')
            self.stdout.flush()


def import_document_from_path(doc_path, group, user):
    filename = os.path.split(doc_path)[1]
    tags, filename = extract_tags(filename)
    name, extension = os.path.splitext(filename)

    name = logic.clean_filename(name)

    document = logic.add_file_to_group(
        file=File(open(doc_path, 'rb')),
        name=name,
        extension=extension,
        group=group,
        tags=tags,
        user=user
    )

    document.add_to_queue()


def extract_tags(filename):
    if ":" not in filename:
        return [], filename

    tags, name = filename.split(":", 1)
    tags = tags.split(',')
    tags = [TAGS.get(x.lower()) for x in tags]
    tags = [tag for tag in tags if tag]

    return tags, name
