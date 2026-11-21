"""Tests for /nowcast, /alerts, /ingest endpoints, and ML inference."""
import pytest
from ml.inference import run_nowcast


@pytest.mark.asyncio
async def test_get_nowcast(client):
    response = await client.get("/nowcast/")
    assert response.status_code == 200
    data = response.json()
    assert "cells" in data or "nowcasts" in data
    if "model" in data and data["model"]:
        assert "ps72" in data["model"].get("name", "")


@pytest.mark.asyncio
async def test_get_alerts(client):
    response = await client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
    assert "count" in data


@pytest.mark.asyncio
async def test_ingest_radar(client):
    response = await client.post("/ingest/radar")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "radar"


@pytest.mark.asyncio
async def test_ingest_lightning(client):
    response = await client.post("/ingest/lightning")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["source"] == "lightning"


@pytest.mark.asyncio
async def test_api_v1_endpoints(client):
    res_nowcast = await client.get("/api/v1/nowcast/")
    assert res_nowcast.status_code == 200

    res_alerts = await client.get("/api/v1/alerts/active")
    assert res_alerts.status_code == 200

    res_metrics = await client.get("/api/v1/metrics")
    assert res_metrics.status_code == 200
    metrics_data = res_metrics.json()
    assert "status" in metrics_data
    assert "metrics" in metrics_data


def test_ml_inference_mode():
    res = run_nowcast(include_demo_cells=True)
    assert res["model"]["mode"] in ["real", "stub"]
    assert "checkpoint_loaded" in res["model"]
    assert len(res["cells"]) >= 3
    for cell in res["cells"]:
        assert len(cell["forecast_positions"]) == 8


def test_ml_inference_empty_when_no_observations():
    res = run_nowcast(include_demo_cells=False)
    assert res["cells"] == []
    assert res["data_sources_used"] == []
    assert res["has_observations"] is False

