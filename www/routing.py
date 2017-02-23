from channels.routing import route
from channels import include
from chat.consumers import chat_receive
from documents.consumers import pad_receive

channel_routing = [
    include("chat.routing.chat_routing", path=r"^/chat"),
    include("documents.routing.pad_routing", path=r"^/pad"),
    route("chat.receive", chat_receive),
    route("pad.receive", pad_receive),
]
