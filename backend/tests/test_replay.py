import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_list_replay_events():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/replay/events")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        ids = [ev["event_id"] for ev in data]
        assert "DEL-2024" in ids
        assert "KOL-2023" in ids
        assert "MUM-2023" in ids


@pytest.mark.asyncio
async def test_get_replay_event_details():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/replay/events/DEL-2024")
        assert res.status_code == 200
        event = res.json()
        assert event["event_id"] == "DEL-2024"
        assert "cells" in event
        assert len(event["cells"]) > 0
        assert "polygon" in event["cells"][0]
        assert "metrics" in event
        assert "csi_35dbz" in event["metrics"]


@pytest.mark.asyncio
async def test_get_replay_raster():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/replay/events/DEL-2024/raster?minute=30")
        assert res.status_code == 200
        assert res.headers["content-type"] == "image/png"
        assert res.content.startswith(PNG_HEADER)
