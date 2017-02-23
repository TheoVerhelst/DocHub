from channels import include

channel_routing = [
    include("chat.routing.chat_routing", path=r"^/chat"),
    include("documents.routing.pad_routing", path=r"^/pad"),
]
