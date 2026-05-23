"""
Virus Scan Service
====================

Scans uploaded files via ClamAV.  Two modes:

1. **Network mode** (recommended for production):
   ClamAV runs on a separate droplet/container.  Files are streamed
   to the ``clamd`` daemon via TCP socket.

2. **Local mode** (for dev/testing):
   Uses ``pyclamd`` to connect to a locally running ``clamd``.

Configuration in settings.py::

    CLAMAV_HOST = "clamav.internal"   # or "127.0.0.1" for local
    CLAMAV_PORT = 3310
    CLAMAV_TIMEOUT = 60               # seconds per scan
    CLAMAV_ENABLED = True             # set False to skip scanning in dev

If ClamAV is unreachable, the scan is marked as ERROR (not CLEAN).
Files with ERROR scan status are flagged for manual review.
"""

from __future__ import annotations

import logging
import socket
import struct
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone

if TYPE_CHECKING:
    from files_management.models import ManagedFile

logger = logging.getLogger(__name__)

# Defaults (override in settings.py)
CLAMAV_HOST = getattr(settings, "CLAMAV_HOST", "127.0.0.1")
CLAMAV_PORT = getattr(settings, "CLAMAV_PORT", 3310)
CLAMAV_TIMEOUT = getattr(settings, "CLAMAV_TIMEOUT", 60)
CLAMAV_ENABLED = getattr(settings, "CLAMAV_ENABLED", True)
CHUNK_SIZE = 8192


class VirusScanService:
    """Scan files for viruses via ClamAV's INSTREAM protocol."""

    @classmethod
    def scan_file(cls, managed_file: ManagedFile) -> dict:
        """
        Scan a ManagedFile.  Updates scan fields on the model and saves.

        Returns:
            {
                "clean": True | False,
                "status": "clean" | "infected" | "scan_error",
                "detail": "OK" | "VirusName FOUND" | error message,
                "engine": "ClamAV",
            }
        """
        from files_management.enums import FileLifecycleStatus, FileScanStatus

        if not CLAMAV_ENABLED:
            logger.info("ClamAV disabled — marking file %s as skipped", managed_file.uuid)
            managed_file.scan_status = FileScanStatus.SKIPPED
            managed_file.scan_completed_at = timezone.now()
            managed_file.scan_engine = "ClamAV (disabled)"
            managed_file.save(update_fields=[
                "scan_status", "scan_completed_at", "scan_engine",
            ])
            return {
                "clean": True,
                "status": "skipped",
                "detail": "ClamAV disabled in settings",
                "engine": "ClamAV",
            }

        # Mark as scanning
        managed_file.scan_status = FileScanStatus.SCANNING
        managed_file.save(update_fields=["scan_status"])

        try:
            # Get the file bytes
            file_bytes = cls._get_file_bytes(managed_file)
            if file_bytes is None:
                raise RuntimeError("Could not read file bytes")

            # Scan via INSTREAM
            result = cls._instream_scan(file_bytes)

            if result["clean"]:
                managed_file.scan_status = FileScanStatus.CLEAN
                managed_file.lifecycle_status = FileLifecycleStatus.ACTIVE
            else:
                managed_file.scan_status = FileScanStatus.INFECTED
                managed_file.lifecycle_status = FileLifecycleStatus.QUARANTINED
                logger.warning(
                    "INFECTED file detected: %s (%s) — %s",
                    managed_file.uuid,
                    managed_file.original_filename,
                    result["detail"],
                )

            managed_file.scan_completed_at = timezone.now()
            managed_file.scan_engine = "ClamAV"
            managed_file.scan_result_detail = result["detail"]
            managed_file.save(update_fields=[
                "scan_status",
                "lifecycle_status",
                "scan_completed_at",
                "scan_engine",
                "scan_result_detail",
            ])

            return result

        except Exception as exc:
            logger.error(
                "Virus scan error for %s: %s",
                managed_file.uuid,
                exc,
            )
            managed_file.scan_status = FileScanStatus.SCANNING
            managed_file.scan_completed_at = timezone.now()
            managed_file.scan_engine = "ClamAV"
            managed_file.scan_result_detail = str(exc)
            managed_file.save(update_fields=[
                "scan_status",
                "scan_completed_at",
                "scan_engine",
                "scan_result_detail",
            ])
            return {
                "clean": False,
                "status": "scan_error",
                "detail": str(exc),
                "engine": "ClamAV",
            }

    @classmethod
    def _instream_scan(cls, file_bytes: bytes) -> dict:
        """
        Send bytes to ClamAV via the INSTREAM protocol.

        Protocol:
            1. Send "zINSTREAM\\0"
            2. Send chunks: [4-byte big-endian length][chunk data]
            3. Send [0x00 0x00 0x00 0x00] to signal end
            4. Read response: "stream: OK\\0" or "stream: VirusName FOUND\\0"
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CLAMAV_TIMEOUT)

        try:
            sock.connect((CLAMAV_HOST, CLAMAV_PORT))

            # Send INSTREAM command
            sock.sendall(b"zINSTREAM\x00")

            # Send file in chunks
            offset = 0
            while offset < len(file_bytes):
                chunk = file_bytes[offset:offset + CHUNK_SIZE]
                chunk_len = struct.pack("!I", len(chunk))
                sock.sendall(chunk_len + chunk)
                offset += CHUNK_SIZE

            # Signal end of stream
            sock.sendall(struct.pack("!I", 0))

            # Read response
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
                if b"\x00" in data:
                    break

            result_str = response.decode("utf-8", errors="replace").strip("\x00").strip()

            if result_str.endswith("OK"):
                return {
                    "clean": True,
                    "status": "clean",
                    "detail": result_str,
                    "engine": "ClamAV",
                }
            elif "FOUND" in result_str:
                return {
                    "clean": False,
                    "status": "infected",
                    "detail": result_str,
                    "engine": "ClamAV",
                }
            else:
                return {
                    "clean": False,
                    "status": "scan_error",
                    "detail": f"Unexpected ClamAV response: {result_str}",
                    "engine": "ClamAV",
                }

        finally:
            sock.close()

    @classmethod
    def _get_file_bytes(cls, managed_file: ManagedFile) -> bytes | None:
        """Read the file bytes — from Django's storage backend."""
        try:
            if managed_file.file:
                managed_file.file.open("rb")
                data = managed_file.file.read()
                managed_file.file.close()
                return data
        except Exception as exc:
            logger.debug("Could not read file via FileField: %s", exc)

        # Fallback: download from Spaces via StorageService
        try:
            from files_management.services.storage_service import StorageService

            client = StorageService._get_client(managed_file.bucket)
            response = client.get_object(
                Bucket=managed_file.bucket.spaces_bucket_name,
                Key=managed_file.storage_key,
            )
            return response["Body"].read()
        except Exception as exc:
            logger.error("Could not download file for scanning: %s", exc)
            return None

    @classmethod
    def ping(cls) -> bool:
        """Check if ClamAV is reachable.  Used by health checks."""
        if not CLAMAV_ENABLED:
            return False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((CLAMAV_HOST, CLAMAV_PORT))
            sock.sendall(b"zPING\x00")
            response = sock.recv(1024)
            sock.close()
            return b"PONG" in response
        except Exception:
            return False