import os
import csv
import time
import socket
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
import httpx
from botocore import UNSIGNED
from botocore.config import Config
import boto3

logger = logging.getLogger(__name__)

from app.core.config import get_settings

settings = get_settings()

RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    socket.gaierror,
    socket.timeout,
    TimeoutError,
)
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 1.5


def with_retries(fn: Callable, *args: Any, **kwargs: Any) -> Any:
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except RETRYABLE_EXCEPTIONS as exc:
            last_exc = exc
            delay = RETRY_BASE_DELAY_SEC * (2 ** (attempt - 1))
            logger.warning(f"Download attempt {attempt} failed: {exc}. Retrying in {delay:.1f}s...")
            time.sleep(delay)
        except Exception as exc:
            logger.error(f"Non-retryable download error: {exc}")
            raise exc
    logger.error(f"All {MAX_RETRIES} download attempts failed.")
    raise last_exc


class AtmosphericDownloader:
    def __init__(self, raw_dir: Optional[str] = None):
        self.raw_dir = raw_dir or settings.data_root
        os.makedirs(self.raw_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.raw_dir, "ingestion_manifest.csv")
        self._init_manifest()

        self._s3_public = boto3.client(
            "s3",
            region_name="us-east-1",
            config=Config(
                signature_version=UNSIGNED,
                read_timeout=15,
                connect_timeout=15,
                retries={"max_attempts": 2},
            ),
        )

    def _init_manifest(self) -> None:
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp_utc",
                    "source",
                    "filename",
                    "file_size_bytes",
                    "md5_hash",
                    "status",
                    "error_message",
                ])

    def log_manifest(
        self,
        source: str,
        filename: str,
        size_bytes: int = 0,
        md5_hash: str = "",
        status: str = "SUCCESS",
        error_msg: str = "",
    ) -> None:
        with open(self.manifest_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                source,
                filename,
                size_bytes,
                md5_hash,
                status,
                error_msg,
            ])

    @staticmethod
    def compute_md5(filepath: str) -> str:
        if not os.path.exists(filepath):
            return ""
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def download_noaa_gfs(self, target_date: datetime, forecast_hour: int = 0) -> Optional[str]:
        date_str = target_date.strftime("%Y%m%d")
        cycle = f"{(target_date.hour // 6) * 6:02d}"
        fhour = f"{forecast_hour:03d}"
        key = f"gfs.{date_str}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.f{fhour}"
        dest_filename = f"gfs_{date_str}_{cycle}z_f{fhour}.grib2"
        dest_dir = os.path.join(self.raw_dir, "nwp")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, dest_filename)

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
            return dest_path

        def _do_download():
            self._s3_public.download_file("noaa-gfs-bdp-pds", key, dest_path)

        try:
            with_retries(_do_download)
            md5 = self.compute_md5(dest_path)
            size = os.path.getsize(dest_path)
            self.log_manifest("NOAA_GFS_AWS", dest_filename, size, md5, "SUCCESS")
            return dest_path
        except Exception as exc:
            self.log_manifest("NOAA_GFS_AWS", dest_filename, 0, "", "FAILED", str(exc))
            return None

    async def download_mosdac_insat(
        self,
        product: str = "3D_IMG_L1B_STD",
        target_time: Optional[datetime] = None,
    ) -> Optional[str]:
        target = target_time or datetime.now(timezone.utc)
        date_str = target.strftime("%Y%m%d_%H%M")
        dest_dir = os.path.join(self.raw_dir, "satellite")
        os.makedirs(dest_dir, exist_ok=True)
        dest_filename = f"insat_{product}_{date_str}.h5"
        dest_path = os.path.join(dest_dir, dest_filename)

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
            return dest_path

        mosdac_user = settings.mosdac_username
        mosdac_pass = settings.mosdac_password

        if not mosdac_user or not mosdac_pass:
            self.log_manifest("MOSDAC_INSAT", dest_filename, 0, "", "CREDENTIALS_REQUIRED", "MOSDAC credentials not configured")
            return None

        mosdac_url = f"https://www.mosdac.gov.in/api/v1/download/{product}/{date_str}"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.get(mosdac_url, auth=(mosdac_user, mosdac_pass))
                if resp.status_code == 200:
                    with open(dest_path, "wb") as f:
                        f.write(resp.content)
                    md5 = self.compute_md5(dest_path)
                    size = os.path.getsize(dest_path)
                    self.log_manifest("MOSDAC_INSAT", dest_filename, size, md5, "SUCCESS")
                    return dest_path
                else:
                    self.log_manifest("MOSDAC_INSAT", dest_filename, 0, "", "HTTP_ERROR", f"Status {resp.status_code}")
                    return None
        except Exception as exc:
            self.log_manifest("MOSDAC_INSAT", dest_filename, 0, "", "FAILED", str(exc))
            return None
