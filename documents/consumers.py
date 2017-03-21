# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import channels
from .models import Document
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user
from channels.sessions import enforce_ordering
from . import pad as pad_ns

def get_pad_group(document):
    """Returns the channel group to which this document belongs."""
    return channels.Group("pad" + document)

def get_user_group(user):
    return channels.Group("pad_user_" + user.netid)


def get_pad(document_pk):
    group = channels.Group("pad" + str(document_pk))
    if not hasattr(group.channel_layer, "pads"):
        group.channel_layer.pads = {}
    pads = group.channel_layer.pads
    document = get_object_or_404(Document, pk=document_pk)
    data = document.original.read().decode("utf-8")
    return pads.setdefault(document_pk, pad_ns.Pad(data))

# Websockets

@enforce_ordering
@channel_session_user_from_http
def ws_pad_connect(message, document_pk):
    """
    Connected to "websocket.connect".
    """
    message.channel_session['document'] = document_pk

    # FIXME This condition is wrong, only admins and the creator of the pad can edit it
    #if get_object_or_404(Document, pk=document_pk).group.slug in (group.slug for group in message.user.following_groups()):

    # Reply with an ACK
    message.reply_channel.send({'accept': True})
    # Add the user to the pad
    get_pad_group(document_pk).add(message.reply_channel)
    get_user_group(message.user).add(message.reply_channel)

    message.reply_channel.send({'text': json.dumps({
        'type': 'sync',
        'content': repr(get_pad(document_pk))
    })})

@enforce_ordering
@channel_session_user
def ws_pad_receive(message):
    """Handles a websocket message by putting it on the message channel.
    The message channel is separated from websocket.message so that the sending
    process/consumer can move on immediately and not spend time waiting for the
    database save and the (slow on some backends) Group.send() call.

    Connected to "websocket.receive".
    """

    # This message will be send with channel to the right pad consumer
    message_data = json.loads(message['text'])
    message_data['document'] = message.channel_session['document']
    message_data['user'] = message.user

    # Send the message to the right channel
    channels.Channel("pad.receive").send(message_data)

@enforce_ordering
@channel_session_user
def ws_pad_disconnect(message):
    """Disconnects a user form a pad.

    Connected to "websocket.disconnect".
    """
    get_pad_group(message.channel_session['document']).discard(message.reply_channel)
    get_user_group(message.user).discard(message.reply_channel)
    get_pad(message.channel_session['document']).cursor_delete(message.user.netid)

# Pad

def pad_receive(message):
    """
    Connected to "pad.receive".
    """
    cursor_id = message['user'].netid
    pad = get_pad(message['document'])

    if message.content['type'] == "seek":
        try:
            true_position = pad.cursor_seek(cursor_id,
                message.content['position'],
                message.content['context'],
                message.content['context_position'])

            get_user_group(message['user']).send({'text': json.dumps({
                  'type' : "seek",
                  'position' : true_position
            })})
        except pad_ns.PadSelectionDenied:
            get_user_group(message['user']).send({'text': json.dumps({
                'type' : "error",
                'cause' : "seek"
            })})
        except pad_ns.PadOutOfSync:
            get_user_group(message['user']).send({'text': json.dumps({
                'type': 'sync',
                'content': repr(pad)
            })})

    elif message.content['type'] == "edit":
        try:
            # We need the old cursor position, in order to send correct patch to
            # the connected users
            old_position = pad.get_cursor_position(cursor_id)
            # Send the message to the group (i.e. all users connected to the pad)
            deletion_count = message.content['deletion']
            if deletion_count > 0:
                deletion_count = pad.remove(cursor_id, deletion_count)

            inserted_string = message.content['insertion']
            if len(inserted_string) > 0:
                pad.insert(cursor_id, inserted_string)

            get_pad_group(message['document']).send({'text': json.dumps({
                'type' : "edit",
                'position' : old_position,
                'deletion' : deletion_count,
                'insertion' : inserted_string
            })})
        # If the user has not a valid cursor, send a seek error
        except pad_ns.PadOutOfSync:
            get_user_group(message['user']).send({'text': json.dumps({
                'type' : "error",
                'cause' : "seek"
            })})

    elif message.content['type'] == "focus_out":
        if pad.cursor_exists(cursor_id):
            pad.cursor_delete(cursor_id)
