import channels
import catalog.models
from django.shortcuts import get_object_or_404
from channels.auth import channel_session_user_from_http, channel_session_user

# Connected to websocket.connect
@channel_session_user_from_http
def ws_connect(message):
    # Extract the group slug from the url
    group_slug = message.content["path"].strip("/").split("/")[-1]
    # Get the instance of the corresponding Group
    group = get_object_or_404(catalog.models.Group, slug=group_slug)
    message.channel_session["group"] = group_slug

    if group in message.user.following_groups():
        # Reply with an ACK
        message.reply_channel.send({"accept": True})

        channels.Group("chat" + group_slug).add(message.reply_channel)

@channel_session_user
def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    channels.Group("chat" + message.channel_session["group"]).send({
        "text": message.user.first_name + "/" + message.content["text"]
    })

# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    channels.Group("chat" + message.channel_session["group"]).discard(message.reply_channel)
