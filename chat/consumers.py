# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import channels
import catalog.models
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import Message


def message_consumer(message):
    """Handles a websocket message by saving it and broadcasting it to all
    connected users.

    Connected to "chat-messages".
    """
    # Save the message in the database
    group_slug = message.content['group']
    chatMessage = Message.objects.create(
        user=message.content['user'],
        group=get_object_or_404(catalog.models.Group, slug=group_slug),
        text=message.content['text']
    )
    # Send the message to the group (i.e. all users connected on the group chat)
    channels.Group("chat" + group_slug).send({'text': chatMessage.dump_json()})

def send_previous_messages(reply_channel, group_slug, limit=20):
    """Sends previous messages of the group chat to a user. It is intended to
    be used when a user connects.
    """
    messages = Message.objects.filter(group__slug=group_slug)[:limit]
    for message in messages:
        reply_channel.send({'text': message.dump_json()})

@channel_session_user_from_http
def ws_connect(message):
    """Handle a websocket connection by adding the user to the group chat and
    sending him previous messages.

    Connected to "websocket.connect".
    """
    # Extract the group slug from the url
    group_slug = message.content['path'].strip("/").split("/")[-1]
    # Get the instance of the corresponding Group
    group = get_object_or_404(catalog.models.Group, slug=group_slug)
    message.channel_session['group'] = group_slug

    if group in message.user.following_groups():
        # Reply with an ACK
        message.reply_channel.send({'accept': True})

        channels.Group("chat" + group_slug).add(message.reply_channel)
        send_previous_messages(message.reply_channel, group_slug)

@channel_session_user
def ws_message(message):
    """Handles a websocket message by putting it on the message channel.
    The message channel is separated from websocket.message so that the sending
    process/consumer can move on immediately and not spend time waiting for the
    database save and the (slow on some backends) Group.send() call.

    Connected to "websocket.receive".
    """
    # Stick the message onto the processing queue
    channels.Channel("chat-messages").send({
        'group': message.channel_session['group'],
        'text': message['text'],
        'user': message.user
    })

@channel_session_user
def ws_disconnect(message):
    """Disconnects a user form a chat group.

    Connected to "websocket.disconnect".
    """
    channels.Group("chat" + message.channel_session['group']).discard(message.reply_channel)
