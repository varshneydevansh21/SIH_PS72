from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from app.websockets.live_feed import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


async def broadcast_nowcast(data: dict):
    await ws_manager.send_to_channel("nowcast", data)
    await ws_manager.broadcast(data)


async def broadcast_alerts(data: dict):
    await ws_manager.send_to_channel("alerts", data)
    await ws_manager.broadcast(data)


@router.websocket("/ws/nowcast")
@router.websocket("/ws/live")
async def nowcast_ws(websocket: WebSocket):
    raw_channels = websocket.query_params.get("channels", "nowcast,alerts,radar,lightning")
    channels = [ch.strip() for ch in raw_channels.split(",") if ch.strip()]
    await ws_manager.connect(websocket, channels)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
