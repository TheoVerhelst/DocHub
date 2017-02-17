from channels import Group
from channels.sessions import channel_session

# Connected to websocket.connect
@channel_session
def ws_connect(message):
    # Reply with an ACK
    message.reply_channel.send({"accept": True})

    group_slug = message.content["path"].strip("/").split("/")[-1]
    message.channel_session["group"] = group_slug

    Group("chat" + group_slug).add(message.reply_channel)

@channel_session
def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    Group("chat" + message.channel_session["group"]).send({
        "text": message.content["text"],
    })

# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("chat" + message.channel_session["group"]).discard(message.reply_channel)
