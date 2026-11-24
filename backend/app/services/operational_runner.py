import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.nowcast_adapter import run_nowcast
from app.services.contouring import ContourExtractor
from app.services.cell_tracking import CellTracker
from app.services.impact_service import ImpactService
from app.services.alert_engine import generate_alerts
from app.api.ws import broadcast_nowcast, broadcast_alerts

logger = logging.getLogger(__name__)


class OperationalRunner:
    def __init__(self):
        self.contour_extractor = ContourExtractor()
        self.cell_tracker = CellTracker()
        self.impact_service = ImpactService()
        self._is_running = False
        self._task: Optional[asyncio.Task] = None
        self._cycle_count = 0
        self._last_run: Optional[Dict[str, Any]] = None
        self._history: List[Dict[str, Any]] = []

    async def execute_cycle(
        self,
        include_demo_cells: bool = False,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        t_start = time.perf_counter()
        cycle_id = f"cyc-{self._cycle_count + 1:05d}"
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        t0 = time.perf_counter()
        nowcast_raw = run_nowcast(include_demo_cells=include_demo_cells)
        t_inference_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        raw_cells = nowcast_raw.get("cells", [])
        enriched_cells = self.cell_tracker.track_and_enrich_cells(raw_cells)

        nowcast_payload = dict(nowcast_raw)
        nowcast_payload["cells"] = enriched_cells
        nowcast_payload["cycle_id"] = cycle_id
        nowcast_payload["issued_at"] = now_iso

        alerts = generate_alerts(nowcast_payload, threshold=0.50)
        t_contour_alerts_ms = (time.perf_counter() - t1) * 1000.0

        t2 = time.perf_counter()
        try:
            await broadcast_nowcast(nowcast_payload)
            await broadcast_alerts({"alerts": alerts, "issued_at": now_iso})
        except Exception as exc:
            logger.error(f"WebSocket broadcast failed: {exc}")
        t_ws_ms = (time.perf_counter() - t2) * 1000.0

        if db is not None:
            try:
                from app.models.nowcast import Nowcast
                import uuid
                record = Nowcast(
                    id=uuid.uuid4(),
                    run_time=now,
                    lead_time_minutes=120,
                    storm_intensity_class=enriched_cells[0]["severity"] if enriched_cells else "minimal",
                    probability=enriched_cells[0]["probability"] if enriched_cells else 0.0,
                    details={"cycle_id": cycle_id, "cell_count": len(enriched_cells)},
                )
                db.add(record)
                await db.commit()
            except Exception as exc:
                logger.warning(f"Failed to persist nowcast cycle {cycle_id} to DB: {exc}")
                await db.rollback()

        total_ms = (time.perf_counter() - t_start) * 1000.0

        latencies = {
            "inference_ms": round(t_inference_ms, 2),
            "contour_and_alerts_ms": round(t_contour_alerts_ms, 2),
            "broadcast_ms": round(t_ws_ms, 2),
            "total_cycle_ms": round(total_ms, 2),
        }

        self._cycle_count += 1
        summary = {
            "cycle_id": cycle_id,
            "status": "success",
            "timestamp": now_iso,
            "latency": latencies,
            "cell_count": len(enriched_cells),
            "alert_count": len(alerts),
            "nowcast": nowcast_payload,
            "alerts": alerts,
        }

        self._last_run = summary
        self._history.append({
            "cycle_id": cycle_id,
            "timestamp": now_iso,
            "total_ms": latencies["total_cycle_ms"],
            "cell_count": len(enriched_cells),
            "alert_count": len(alerts),
        })
        if len(self._history) > 50:
            self._history.pop(0)

        return summary

    async def _loop(self, interval_seconds: int):
        self._is_running = True
        while self._is_running:
            try:
                await self.execute_cycle(include_demo_cells=False)
            except Exception as exc:
                logger.error(f"Error in operational nowcast loop: {exc}")
            try:
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
        self._is_running = False

    def start_scheduler(self, interval_seconds: int = 900):
        if self._is_running and self._task and not self._task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._loop(interval_seconds))

    def stop_scheduler(self):
        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()

    def get_status(self) -> Dict[str, Any]:
        avg_latency = (
            round(sum(h["total_ms"] for h in self._history) / len(self._history), 2)
            if self._history
            else 0.0
        )
        return {
            "scheduler_running": self._is_running,
            "cycle_count": self._cycle_count,
            "last_cycle": self._last_run["cycle_id"] if self._last_run else None,
            "last_timestamp": self._last_run["timestamp"] if self._last_run else None,
            "last_latency_ms": self._last_run["latency"]["total_cycle_ms"] if self._last_run else None,
            "average_latency_ms": avg_latency,
            "recent_cycles": self._history[-10:],
        }


operational_runner = OperationalRunner()
