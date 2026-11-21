import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {
            "nowcast": set(),
            "alerts": set(),
            "radar": set(),
            "lightning": set(),
        }

    async def connect(self, websocket: WebSocket, channels: list[str] = None):
        await websocket.accept()
        self.active_connections.add(websocket)
        if channels:
            for ch in channels:
                if ch in self.channel_subscriptions:
                    self.channel_subscriptions[ch].add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        for subs in self.channel_subscriptions.values():
            subs.discard(websocket)

    async def broadcast(self, data: dict):
        if not self.active_connections:
            return
        msg = json.dumps(data)
        stale = []
        for ws in self.active_connections:
            try:
                await ws.send_text(msg)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

    async def send_to_channel(self, channel: str, data: dict):
        subs = self.channel_subscriptions.get(channel, set())
        if not subs:
            return
        msg = json.dumps({"channel": channel, "data": data})
        stale = []
        for ws in subs:
            try:
                await ws.send_text(msg)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)


manager = WebSocketManager()
