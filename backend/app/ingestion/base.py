"""
SIH PS072 - Data Ingestion Base Interface

Abstract base class for all data source ingestors.
Every new data source (Radar, Satellite, Lightning, NWP) inherits from this
and implements `fetch()` and `process()`.

Design rationale:
  In FreeLangX you had a clean start/stop lifecycle per audio stream.
  Here we replicate that pattern for data streams — each ingestor has
  its own async fetch→process→store pipeline with health tracking.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataSourceStatus:
    """Tracks the health/heartbeat of an individual data source."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.last_fetch_at: Optional[datetime] = None
        self.last_success_at: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.total_fetches: int = 0
        self.total_errors: int = 0

    def record_success(self):
        now = datetime.now(timezone.utc)
        self.last_fetch_at = now
        self.last_success_at = now
        self.total_fetches += 1

    def record_error(self, error: str):
        self.last_fetch_at = datetime.now(timezone.utc)
        self.last_error = error
        self.total_fetches += 1
        self.total_errors += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_name,
            "last_fetch_at": self.last_fetch_at.isoformat() if self.last_fetch_at else None,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_error": self.last_error,
            "total_fetches": self.total_fetches,
            "total_errors": self.total_errors,
            "healthy": self.last_error is None or (
                self.last_success_at is not None
                and self.last_success_at == self.last_fetch_at
            ),
        }


class BaseIngestor(ABC):
    """
    Abstract base for all data source ingestors.

    Subclasses must implement:
        fetch()   — pull raw data from the external API/file source
        process() — parse, validate, and normalize raw data into internal format

    The `run()` method orchestrates the full pipeline with error handling.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.status = DataSourceStatus(source_name)
        logger.info("Ingestor initialised: {}", source_name)

    @abstractmethod
    async def fetch(self) -> Any:
        """
        Fetch raw data from the external source.
        Returns raw bytes, file path, or parsed dict depending on source.
        """
        ...

    @abstractmethod
    async def process(self, raw_data: Any) -> Any:
        """
        Process raw data into a normalised internal representation.
        Typically returns an xarray.Dataset, numpy array, or Pydantic model.
        """
        ...

    async def store(self, processed_data: Any) -> None:
        """
        Optional: persist processed data to the database or cache.
        Override in subclass if needed. Default is no-op.
        """
        pass

    async def run(self) -> Optional[Any]:
        """
        Full ingestion pipeline: fetch → process → store.
        Handles errors gracefully and tracks health status.
        """
        try:
            logger.info("⬇  [{}] Fetching data...", self.source_name)
            raw = await self.fetch()

            if raw is None:
                logger.warning("[{}] Fetch returned None — skipping cycle", self.source_name)
                return None

            logger.info("⚙  [{}] Processing data...", self.source_name)
            processed = await self.process(raw)

            await self.store(processed)

            self.status.record_success()
            logger.success("✅ [{}] Ingestion cycle complete", self.source_name)
            return processed

        except Exception as e:
            self.status.record_error(str(e))
            logger.error("❌ [{}] Ingestion failed: {}", self.source_name, e)
            return None
