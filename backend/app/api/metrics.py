"""GET /api/v1/metrics -- Model skill scores & evaluation metrics."""
import json
import os
from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["metrics"])

METRICS_PATH = "ml/configs/evaluation_metrics.json"


@router.get("/metrics")
async def get_metrics() -> dict:
    """Returns the latest evaluated or pilot metrics report for the nowcasting model."""
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "model": "UNet-ConvLSTM",
        "status": "uncalibrated_pilot",
        "num_test_samples": 0,
        "metrics": {
            "CSI": None,
            "POD": None,
            "FAR": None,
            "HSS": None,
            "RMSE_position_km": None,
        },
        "targets_met": {
            "all_targets_met": False,
            "notes": "Model evaluation in progress.",
        },
    }
