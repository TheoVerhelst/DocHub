from channels import Group

# Connected to websocket.connect
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    Group("chat").add(message.reply_channel)

def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    Group("chat").send({
        "text": message.content['text'],
    })

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)
