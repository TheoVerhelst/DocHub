from channels.routing import route
from chat.consumers import ws_receive, ws_connect, ws_disconnect, chat_receive

channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_receive),
    route("websocket.disconnect", ws_disconnect),
    route("chat.receive", chat_receive),
]
