from channels.routing import route
from .consumers import ws_connect, ws_vote, ws_disconnect

websocket_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_vote),
    route("websocket.disconnect", ws_disconnect),
]