# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import channels
from .models import Document
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user

# Websockets

@channel_session_user_from_http
def ws_pad_connect(message, document_pk):
    """
    Connected to "websocket.connect".
    """
    # Get the instance of the corresponding Group
    group = get_object_or_404(Document, pk=document_pk)
    message.channel_session['document'] = document_pk

    # TODO: check if user is in the group of the document
    if True:
        # Reply with an ACK
        message.reply_channel.send({'accept': True})

        # Add the user to the chat group
        channels.Group("pad" + document_pk).add(message.reply_channel)

@channel_session_user
def ws_pad_receive(message):
    """Handles a websocket message by putting it on the message channel.
    The message channel is separated from websocket.message so that the sending
    process/consumer can move on immediately and not spend time waiting for the
    database save and the (slow on some backends) Group.send() call.

    Connected to "websocket.receive".
    """

    message_data = json.load(message['text'])
    # Stick the message onto the processing queue
    channels.Channel("pad.receive").send({
        'document': message.channel_session['document'],
        'position': message_data['position'],
        'character': message_data['character'],
        'user': message.user
    })

@channel_session_user
def ws_pad_disconnect(message):
    """Disconnects a user form a pad.

    Connected to "websocket.disconnect".
    """
    channels.Group("pad" + message.channel_session['document']).discard(message.reply_channel)


# Pad

def pad_receive(message):
    """Handles a websocket message by saving it and broadcasting it to all
    connected users.

    Connected to "chat.receive".
    """
    document_pk = message.content['document']
    # Send the message to the group (i.e. all users connected on the group chat)
    channels.Group("pad" + document_pk).send({'text': json.dumps({
        'position' : message.content['position'],
        'character' : message.content['character']
    })})
