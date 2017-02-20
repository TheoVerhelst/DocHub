# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import channels
import catalog.models
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import Message


# Connected to chat-messages
def message_consumer(message):
    # Save to model
    group_slug = message.content['group']
    Message.objects.create(
        user=message.content['user'],
        group=message.content['group'],
        text=message.content['text']
    )
    # Broadcast to listening sockets
    channels.Group("chat" + group_slug).send({
        'text': message.content['user'].first_name + "/" + message.content['text'],
    })

# Connected to websocket.connect
@channel_session_user_from_http
def ws_connect(message):
    # Extract the group slug from the url
    group_slug = message.content['path'].strip("/").split("/")[-1]
    # Get the instance of the corresponding Group
    group = get_object_or_404(catalog.models.Group, slug=group_slug)
    message.channel_session['group'] = group_slug

    if group in message.user.following_groups():
        # Reply with an ACK
        message.reply_channel.send({'accept': True})

        channels.Group("chat" + group_slug).add(message.reply_channel)

@channel_session_user
def ws_message(message):
    # Stick the message onto the processing queue
    channels.Channel("chat-messages").send({
        'group': message.channel_session['group'],
        'text': message['text'],
        'user': message.user
    })

# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    channels.Group("chat" + message.channel_session['group']).discard(message.reply_channel)
