"""
SIH PS072 - WebSocket Live Feed Manager

Real-time push of nowcast updates to connected frontend clients.
Mirrors the WebSocket architecture from your FreeLangX offscreen.js:
  - offscreen.js maintained a socket to your Render backend
  - Here the server IS the WebSocket host, pushing to N browser clients

Supports:
  - Multiple concurrent client connections
  - Channel-based subscriptions (radar, lightning, alerts, nowcast)
  - Automatic reconnection guidance via close codes
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


websocket_router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections and channel subscriptions.

    Similar to how your FreeLangX background.js tracked `activeTabId`
    to route subtitles to the right tab — here we track which clients
    are subscribed to which data channels.
    """

    def __init__(self):
        # channel_name → set of connected WebSocket clients
        self._subscriptions: Dict[str, Set[WebSocket]] = {
            "radar": set(),
            "lightning": set(),
            "nowcast": set(),
            "alerts": set(),
        }
        # All active connections for broadcast
        self._active: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, channels: List[str]):
        """Accept a new client and subscribe it to requested channels."""
        await websocket.accept()
        self._active.add(websocket)

        for ch in channels:
            if ch in self._subscriptions:
                self._subscriptions[ch].add(websocket)

        logger.info(f"Client connected (total={len(self._active)}). Channels: {channels}")

    def disconnect(self, websocket: WebSocket):
        """Remove a client from all subscriptions."""
        self._active.discard(websocket)
        for subscribers in self._subscriptions.values():
            subscribers.discard(websocket)
        logger.info(f"Client disconnected (remaining={len(self._active)})")

    async def send_to_channel(self, channel: str, data: dict):
        """Push a message to all clients subscribed to a channel."""
        subscribers = self._subscriptions.get(channel, set())
        if not subscribers:
            return

        payload = json.dumps({
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        })

        dead_connections = []
        for ws in subscribers:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_connections.append(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(ws)

    async def broadcast(self, data: dict):
        """Push a message to ALL connected clients (e.g., system alerts)."""
        payload = json.dumps({
            "channel": "system",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        })

        dead_connections = []
        for ws in self._active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(ws)

    @property
    def active_count(self) -> int:
        return len(self._active)


# ─── Singleton Manager ──────────────────────────────────────
ws_manager = ConnectionManager()


# ─── WebSocket Endpoint ─────────────────────────────────────
@websocket_router.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    """
    Main WebSocket endpoint for the frontend dashboard.

    Query params:
        channels: comma-separated list of channels to subscribe to.
                  e.g., ws://localhost:8000/ws/live?channels=radar,lightning,nowcast

    The client receives JSON messages shaped as:
    {
        "channel": "lightning",
        "timestamp": "2026-09-26T10:30:00Z",
        "data": { ... }
    }
    """
    # Parse requested channels from query params
    raw_channels = websocket.query_params.get("channels", "nowcast,alerts")
    channels = [ch.strip() for ch in raw_channels.split(",") if ch.strip()]

    await ws_manager.connect(websocket, channels)

    try:
        while True:
            # Keep the connection alive; optionally handle client messages
            message = await websocket.receive_text()

            # Handle ping/pong or client-side commands
            try:
                parsed = json.loads(message)
                if parsed.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif parsed.get("type") == "subscribe":
                    # Dynamic subscription changes
                    new_channels = parsed.get("channels", [])
                    for ch in new_channels:
                        if ch in ws_manager._subscriptions:
                            ws_manager._subscriptions[ch].add(websocket)
                    logger.info(f"Client updated subscriptions: +{new_channels}")
            except json.JSONDecodeError:
                pass  # Ignore non-JSON messages

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
