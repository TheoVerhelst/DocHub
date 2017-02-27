# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import channels
from .models import Document
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user

def get_pad_from_message(message):
    """Returns the channel group to which this message belongs."""
    if hasattr(message, channel_session):
        return channels.Group("pad" + message.channel_session['document'])
    elif hasattr(message, content):
        return channels.Group("pad" + message.content['document'])

# Websockets

@channel_session_user_from_http
def ws_pad_connect(message, document_pk):
    """
    Connected to "websocket.connect".
    """
    message.channel_session['document'] = document_pk

    if get_object_or_404(Document, pk=document_pk).group.slug in (group.slug for group in message.user.following_groups()):
        # Reply with an ACK
        message.reply_channel.send({'accept': True})
        # Add the user to the pad
        get_pad_from_message(message).add(message.reply_channel)

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


@channel_session_user
def ws_pad_disconnect(message):
    """Disconnects a user form a pad.

    Connected to "websocket.disconnect".
    """
    get_pad_from_message(message).discard(message.reply_channel)
    # DISCONNECT IN PAD

# Pad

def pad_receive(message):
    """
    Connected to "pad.receive".
    """

    if message_data['type'] == "seek":
        # CONNECT IN PAD
        pass

    elif message_data['type'] == "edit":
        # Send the message to the group (i.e. all users connected to the pad)
        # EDIT IN PAD
        get_pad_from_message(message).send({'text': json.dumps({
        })})

    elif message_data['type'] == "focus_out":
        pass
        # DISCONNECT IN PAD
