"""
Requests API consumer.
- Sends requests with exponential retry
- Does not retry 4xx errors (definitive)
- Retries 5xx and connection errors (temporary)
- JSON structured logs
"""
import json
import logging
import os
import random
import time
import sys
import uuid
import httpx
from datetime import datetime, timezone
from typing import Any, Optional


# ── Structured JSON logging ─────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    SERVICE = "requests-consumer"

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.SERVICE,
            "message": record.getMessage(),
        }
        for field in (
            "external_id",
            "request_id",
            "attempt",
            "max_attempts",
            "status_code",
            "duration_ms",
            "error",
            "endpoint",
            "method",
        ):
            val = getattr(record, field, None)
            if val is not None:
                entry[field] = val

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("consumer")


# ── Configuration ─────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "5"))
BASE_DELAY_S = float(os.getenv("BASE_DELAY_S", "1.0"))
MAX_DELAY_S = float(os.getenv("MAX_DELAY_S", "30.0"))
TIMEOUT_S = float(os.getenv("TIMEOUT_S", "10.0"))
STARTUP_WAIT_S = float(os.getenv("STARTUP_WAIT_S", "5.0"))


# ── Example requests ────────────────────────────────────────────────────

APPLICATIONS: list[dict] = [
    {
        "external_id": "468a329d-48ef-4171-8bc6-92d525752945",
        "type": "technical_support",
        "requester_name": "Ana Martínez",
        "email": "ana.martinez@institucion.edu.co",
        "description": "I cannot access the grading system since yesterday morning",
        "priority": "high",
    },
    {
        "external_id": "b28b6d41-768f-410a-b36e-519280145c22",
        "type": "platform_access",
        "requester_name": "Carlos Pérez",
        "email": "carlos.perez@institucion.edu.co",
        "description": "I need access to the financial reports module on the third floor",
        "priority": "medium",
    },
    {
        "external_id": "f491c10d-2b4a-4638-baef-034720970db1",
        "type": "academic",
        "requester_name": "Laura Gómez",
        "email": "laura.gomez@institucion.edu.co",
        "description": "Grade correction request for the second semester according to the attached act",
        "priority": "high",
    },
    {
        "external_id": "e78b7bdf-1b4e-4b2a-8287-c3732ab2f9a6",
        "type": "administrative",
        "requester_name": "Juan Rodríguez",
        "email": "juan.rodriguez@institucion.edu.co",
        "description": "Clearance request for graduation process, urgent response required",
        "priority": "low",
    },
    {
        "external_id": "c8d9e6e3-2e45-42a1-bd88-0f1c37b75249",
        "type": "technical_support",
        "requester_name": "María López",
        "email": "maria.lopez@institucion.edu.co",
        "description": "The computer in lab 3 won't turn on since Tuesday afternoon",
        "priority": "medium",
    },
    # Intentionally invalid request to test 4xx error handling
    {
        "external_id": "a58b29f7-6b4d-4591-9e76-d384c7590d34",
        "type": "invalid_type",           # non-existent catalog value
        "requester_name": "Test Error",
        "email": "not-an-email",          # invalid email
        "description": "Error test",
        "priority": "urgent",             # non-existent priority
    },
]


def http_post(url: str, payload: dict, timeout: float, correlation_id: str = "") -> tuple[int, dict]:
    req_id = correlation_id or str(uuid.uuid4())
    headers = {"X-Request-ID": req_id}
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            body = resp.json()
            return resp.status_code, body
    except httpx.HTTPStatusError as e:
        body = e.response.json() if e.response.content else {}
        return e.response.status_code, body
    except httpx.RequestError as e:
        # Re-raise as RequestError for the caller
        raise e

def http_get(url: str, timeout: float, correlation_id: str = "") -> tuple[int, dict]:
    req_id = correlation_id or str(uuid.uuid4())
    headers = {"X-Request-ID": req_id}
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url, headers=headers)
            body = resp.json()
            return resp.status_code, body
    except httpx.HTTPStatusError as e:
        body = e.response.json() if e.response.content else {}
        return e.response.status_code, body
    except httpx.RequestError as e:
        raise e


# ── Retry logic ───────────────────────────────────────────────────────────

def _is_retryable(status_code: Optional[int]) -> bool:
    """5xx and None (connection error) are temporary → retry."""
    if status_code is None:
        return True
    return status_code >= 500


def _backoff_delay(attempt: int) -> float:
    """Exponential delay with jitter: min(base * 2^attempt + jitter, max)."""
    delay = BASE_DELAY_S * (2 ** attempt) + random.uniform(0, 1)
    return min(delay, MAX_DELAY_S)


def post_with_retry(
    url: str,
    payload: dict,
    identifier: str,
) -> Optional[dict]:
    last_status: Optional[int] = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.perf_counter()
        status_code: Optional[int] = None

        try:
            status_code, body = http_post(url, payload, TIMEOUT_S, identifier)
            duration = int((time.perf_counter() - start) * 1000)

            if status_code in (200, 201):
                log.info(
                    "ServiceRequest successfully created",
                    extra={
                        "external_id": identifier,
                        "request_id": body.get("external_id"),
                        "attempt": attempt,
                        "status_code": status_code,
                        "duration_ms": duration,
                        "method": "POST",
                        "endpoint": url,
                    },
                )
                return body

            # 4xx Error → definitive, do not retry
            if 400 <= status_code < 500:
                log.warning(
                    "Definitive error (4xx), will not retry",
                    extra={
                        "external_id": identifier,
                        "attempt": attempt,
                        "status_code": status_code,
                        "error": body.get("detail", "Client error"),
                        "method": "POST",
                        "endpoint": url,
                    },
                )
                return None

            # 5xx Error → temporary, retry
            log.warning(
                "Temporary error (5xx), retrying",
                extra={
                    "external_id": identifier,
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "status_code": status_code,
                    "error": body.get("detail", "Server error"),
                },
            )

        except (httpx.RequestError, TimeoutError, OSError) as exc:
            duration = int((time.perf_counter() - start) * 1000)
            log.warning(
                "Connection error, retrying",
                extra={
                    "external_id": identifier,
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "error": str(exc),
                    "duration_ms": duration,
                },
            )

        last_status = status_code
        if attempt < MAX_ATTEMPTS:
            delay = _backoff_delay(attempt)
            log.info(
                f"Waiting {delay:.1f}s before next attempt",
                extra={
                    "external_id": identifier,
                    "attempt": attempt,
                },
            )
            time.sleep(delay)

    log.error(
        "Max retries exceeded",
        extra={
            "external_id": identifier,
            "max_attempts": MAX_ATTEMPTS,
            "last_status_code": last_status,
        },
    )
    return None


# ── Main flow ───────────────────────────────────────────────────────────

def wait_for_backend() -> None:
    """Active wait until backend responds on /health."""
    health_url = f"{API_BASE_URL.replace('/api/v1', '')}/health"
    log.info("Waiting for backend to be ready", extra={"endpoint": health_url})

    for attempt in range(1, 31):
        try:
            status_code, _ = http_get(health_url, timeout=3.0)
            if status_code == 200:
                log.info("Backend is ready", extra={"attempt": attempt})
                return
        except Exception:
            pass

        log.info(
            "Backend not ready yet, retrying...",
            extra={"attempt": attempt},
        )
        time.sleep(3)

    raise RuntimeError("Backend did not respond after 90 seconds")


def fetch_status(request_id: str) -> Optional[dict]:
    url = f"{API_BASE_URL}/requests/{request_id}"
    try:
        status_code, body = http_get(url, timeout=TIMEOUT_S, correlation_id=request_id)
        if status_code == 200:
            log.info(
                "Status fetched",
                extra={
                    "request_id": request_id,
                    "status_code": status_code,
                    "method": "GET",
                    "endpoint": url,
                },
            )
            return body
        log.warning(
            "Could not fetch status",
            extra={"request_id": request_id, "status_code": status_code},
        )
    except Exception as exc:
        log.error(
            "Error fetching status",
            extra={"request_id": request_id, "error": str(exc)},
        )
    return None


def main() -> None:
    log.info("Starting requests consumer")
    time.sleep(STARTUP_WAIT_S)
    wait_for_backend()

    create_url = f"{API_BASE_URL}/requests"
    results: list[dict] = []

    # ── Phase 1: create all requests ──────────────────────────────────
    log.info(f"Starting creation of {len(APPLICATIONS)} requests")

    for request in APPLICATIONS:
        identifier = request["external_id"]
        log.info("Sending request", extra={"external_id": identifier})
        result = post_with_retry(create_url, request, identifier)
        if result:
            results.append(result)

    log.info(
        "Creation phase completed",
        extra={"created_count": len(results), "failed": len(APPLICATIONS) - len(results)},
    )

    if not results:
        log.error("No request was successfully created.")
        sys.exit(1)

    # ── Phase 2: check status of created ones ───────────────────────────────
    log.info("Checking the status of created requests")
    time.sleep(2)

    for item in results:
        current_status = fetch_status(item["external_id"])
        if current_status:
            log.info(
                "Summary request",
                extra={
                    "request_id": item["external_id"],
                    "external_id": item["external_id"],
                    "status": current_status["status"],
                    "priority": current_status["priority"],
                },
            )

    log.info("Consumer successfully completed")


if __name__ == "__main__":
    main()
