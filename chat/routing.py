from channels.routing import route
from .consumers import ws_chat_connect, ws_chat_receive, ws_chat_disconnect, chat_receive

chat_routing = [
    route("websocket.connect", ws_chat_connect, path=r"^/(?P<group_slug>[^/]+)/$"),
    route("websocket.receive", ws_chat_receive),
    route("websocket.disconnect", ws_chat_disconnect),
]
