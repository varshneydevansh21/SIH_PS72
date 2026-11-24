import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.raster_service import RasterService

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def test_raster_service_generate_png():
    svc = RasterService()
    png_bytes = svc.generate_raster_png(minute=0, layer="composite", width=128, height=128)
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 100
    assert png_bytes.startswith(PNG_HEADER)


def test_raster_service_decay_and_layers():
    svc = RasterService()
    for layer in ["composite", "thunderstorm", "lightning"]:
        for minute in [0, 45, 120]:
            data = svc.generate_raster_png(minute=minute, layer=layer, width=64, height=64)
            assert data.startswith(PNG_HEADER)


@pytest.mark.asyncio
async def test_api_raster_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/nowcast/raster?minute=30&layer=composite&width=128&height=128")
        assert res.status_code == 200
        assert res.headers["content-type"] == "image/png"
        assert res.content.startswith(PNG_HEADER)
