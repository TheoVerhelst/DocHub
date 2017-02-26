# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import channels
import catalog.models
from django.shortcuts import get_object_or_404
from django.utils import html
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import Message

def get_chat_from_message(message):
    """Returns the channel group to which this message belongs."""
    return channels.Group("chat" + message.channel_session['group'])

# Websockets

@channel_session_user_from_http
def ws_chat_connect(message, group_slug):
    """Handle a websocket connection by adding the user to the group chat and
    sending him previous messages.

    Connected to "websocket.connect".
    """
    message.channel_session['group'] = group_slug

    if group_slug in (group.slug for group in message.user.following_groups()):
        # Reply with an ACK
        message.reply_channel.send({'accept': True})

        # Add the user to the chat group
        get_chat_from_message(message).add(message.reply_channel)

@channel_session_user
def ws_chat_receive(message):
    """Handles a websocket message by putting it on the message channel.
    The message channel is separated from websocket.message so that the sending
    process/consumer can move on immediately and not spend time waiting for the
    database save and the (slow on some backends) Group.send() call.

    Connected to "websocket.receive".
    """
    # Refuse empty message
    if len(message['text']) > 0:
        # Stick the message onto the processing queue
        channels.Channel("chat.receive").send({
            'group': message.channel_session['group'],
            'text': message['text'],
            'user': message.user
        })

@channel_session_user
def ws_chat_disconnect(message):
    """Disconnects a user form a chat group.

    Connected to "websocket.disconnect".
    """
    get_chat_from_message(message).discard(message.reply_channel)


# Chat

def chat_receive(message):
    """Handles a websocket message by saving it and broadcasting it to all
    connected users.

    Connected to "chat.receive".
    """
    # Save the message in the database
    group_slug = message.content['group']
    chatMessage = Message.objects.create(
        user=message.content['user'],
        group=get_object_or_404(catalog.models.Group, slug=group_slug),
        text=message.content['text']
    )
    # Escape the text before sending it, so that no XSS injection is possible
    # But we don't need to escape it before saving in database, since Django
    # escapes everything
    chatMessage.text = html.escape(chatMessage.text)
    # Send the message to the group (i.e. all users connected on the group chat)
    channels.Group("chat" + group_slug).send({'text': chatMessage.dump_json()})
