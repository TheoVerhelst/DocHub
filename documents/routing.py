from channels.routing import route
from .consumers import ws_pad_connect, ws_pad_receive, ws_pad_disconnect, pad_receive

pad_routing = [
    route("websocket.connect", ws_pad_connect, path=r"^/(?P<document_pk>[^/]+)/$"),
    route("websocket.receive", ws_pad_receive),
    route("websocket.disconnect", ws_pad_disconnect),
    route("pad.receive", pad_receive),
]
