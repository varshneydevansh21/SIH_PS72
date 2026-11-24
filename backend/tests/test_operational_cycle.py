import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.operational_runner import OperationalRunner


@pytest.mark.asyncio
async def test_operational_runner_execute_cycle():
    runner = OperationalRunner()
    result = await runner.execute_cycle(include_demo_cells=True)
    assert result["status"] == "success"
    assert "cycle_id" in result
    assert "latency" in result

    latencies = result["latency"]
    assert "inference_ms" in latencies
    assert "contour_and_alerts_ms" in latencies
    assert "total_cycle_ms" in latencies
    assert latencies["total_cycle_ms"] < 10000.0

    status = runner.get_status()
    assert status["cycle_count"] == 1
    assert status["last_cycle"] == result["cycle_id"]


@pytest.mark.asyncio
async def test_api_nowcast_status():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/nowcast/status")
        assert res.status_code == 200
        data = res.json()
        assert "scheduler_running" in data
        assert "cycle_count" in data


@pytest.mark.asyncio
async def test_api_nowcast_trigger():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/nowcast/trigger?include_demo=true")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "cycle" in data
        assert data["cycle"]["status"] == "success"
        assert "latency" in data["cycle"]


def test_scheduler_lifecycle():
    runner = OperationalRunner()
    assert not runner._is_running
    runner.stop_scheduler()
    assert not runner._is_running
