# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import unicodedata
import tempfile

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F

from actstream import action

from documents.models import Document
from catalog.models import Group
from documents.forms import UploadFileForm, FileForm, MultipleUploadFileForm, ReUploadForm, PadForm
from telepathy.forms import NewThreadForm
from tags.models import Tag
from documents import logic


@login_required
def upload_file(request, slug):
    group = get_object_or_404(Group, slug=slug)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            if 'file' in request.FILES:
                file = request.FILES['file']
            else:
                filename = "New Document.md"
                open(filename, 'w').close()
                file = open(filename, 'r')
                # Django needs a size attribute to save the file
                file.size = 0


            name, extension = os.path.splitext(file.name)
            name = logic.clean_filename(name)

            if form.cleaned_data['name']:
                name = form.cleaned_data['name']

            document = logic.add_file_to_group(
                file=file,
                name=name,
                extension=extension,
                group=group,
                tags=form.cleaned_data['tags'],
                user=request.user
            )

            document.description = form.cleaned_data['description']
            document.save()

            document.add_to_queue()

            # Delete temp file
            try:
                os.remove(filename)
            except:
                pass

            return HttpResponseRedirect(reverse('group_show', args=[group.slug]))

    else:
        form = UploadFileForm()

    multiform = MultipleUploadFileForm()

    return render(request, 'documents/document_upload.html', {
        'form': form,
        'multiform': multiform,
        'group': group,
    })


@login_required
def upload_multiple_files(request, slug):
    group = get_object_or_404(Group, slug=slug)

    if request.method == 'POST':
        form = MultipleUploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            for attachment in form.cleaned_data['files']:
                name, extension = os.path.splitext(attachment.name)
                name = logic.clean_filename(name)

                document = logic.add_file_to_group(
                    file=attachment,
                    name=name,
                    extension=extension,
                    group=group,
                    tags=[],
                    user=request.user
                )
                document.add_to_queue()

            return HttpResponseRedirect(reverse('group_show', args=[group.slug]))
    return HttpResponseRedirect(reverse('document_put', args=(group.slug,)))


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, id=pk)

    if not request.user.write_perm(obj=doc):
        return HttpResponse('You may not edit this document.', status=403)

    if request.method == 'POST':
        form = FileForm(request.POST)

        if form.is_valid():
            doc.name = form.cleaned_data['name']
            doc.description = form.cleaned_data['description']

            doc.tags.clear()
            for tag in form.cleaned_data['tags']:
                doc.tags.add(Tag.objects.get(name=tag))

            doc.save()

            action.send(request.user, verb="a édité", action_object=doc, target=doc.group)

            return HttpResponseRedirect(reverse('document_show', args=[doc.id]))

    else:
        form = FileForm({
            'name': doc.name,
            'description': doc.description,
            'tags': doc.tags.all()
        })

    return render(request, 'documents/document_edit.html', {
        'form': form,
        'doc': doc,
    })


@login_required
def document_reupload(request, pk):
    document = get_object_or_404(Document, pk=pk)
    template_name = 'documents/document_reupload.html'

    if not request.user.write_perm(obj=document):
        return HttpResponse('You may not edit this document.', status=403)

    if document.state != "DONE":
        return HttpResponse('You may not edit this document while it is processing.', status=403)

    if request.method == 'POST':
        if document.is_pad():
            form = PadForm(request.POST)
        else:
            form = ReUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # If the document is a pad, we simulate an upload by creating
            # a temp file with the pad's content, opening it and giving it to
            # Django as if it was uploaded in the form
            if document.is_pad():

                tmpfile = tempfile.NamedTemporaryFile("w+")
                tmpfile.write(form.cleaned_data['text'])
                tmpfile.flush()

                # Open the temp file for Django to simulate an uploaded file
                file = open(tmpfile.name, 'r')
                # Django needs a size attribute to save the file
                file.size = 0
            else:
                file = request.FILES['file']

            name, extension = os.path.splitext(file.name)

            document.pdf.delete(save=False)
            document.original.delete(save=False)

            document.original.save(str(uuid.uuid4()) + extension, file)

            document.state = "PREPARING"
            document.save()

            document.reprocess(force=True)

            action.send(
                request.user,
                verb="a uploadé une nouvelle version de",
                action_object=document,
                target=document.group
            )

            # Delete temp file
            try:
                os.remove(file.name)
            except:
                pass

            return HttpResponseRedirect(reverse('group_show', args=(document.group.slug,)))

    else:
        if document.is_pad():
            template_name = 'documents/document_pad.html'
            form = PadForm()
        else:
            form = ReUploadForm()

    return render(request, template_name, {'form': form, 'document': document})


@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    body = doc.pdf.read()
    safe_name = unicodedata.normalize("NFKD", doc.name)

    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; filename="%s.pdf"' % safe_name).encode("ascii", "ignore")

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


@login_required
def document_download_original(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    body = doc.original.read()
    safe_name = unicodedata.normalize("NFKD", doc.name)

    response = HttpResponse(body, content_type='application/octet-stream')
    response['Content-Description'] = 'File Transfer'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'attachment; filename="{}{}"'.format(safe_name, doc.file_type).encode("ascii", "ignore")

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


@login_required
def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if document.state != "DONE":
        return HttpResponseRedirect(reverse('group_show', args=(document.group.slug,)))

    context = {
        "document": document,
        "form": NewThreadForm(),
    }

    document.views = F('views') + 1
    document.save(update_fields=['views'])

    return render(request, "documents/viewer.html", context)
