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

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    pg_user = os.getenv("POSTGRES_USER")
    pg_pass = os.getenv("POSTGRES_PASSWORD")
    pg_host = os.getenv("POSTGRES_HOST")
    pg_db = os.getenv("POSTGRES_DB")
    if pg_user and pg_pass and pg_host and pg_db:
        DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}/{pg_db}"
    else:
        DATABASE_URL = "postgresql://test:test@localhost:5432/test"


# ── Example requests ────────────────────────────────────────────────────

SOLICITUDES: list[dict] = [
    {
        "external_id": "11111111-1111-4111-a111-111111111111",
        "type": "technical_support",
        "requester_name": "Ana Martínez",
        "email": "ana.martinez@institucion.edu.co",
        "description": "No puedo acceder al sistema de notas desde ayer en la mañana",
        "priority": "high",
    },
    {
        "external_id": "22222222-2222-4222-a222-222222222222",
        "type": "platform_access",
        "requester_name": "Carlos Pérez",
        "email": "carlos.perez@institucion.edu.co",
        "description": "Necesito acceso al módulo de reportes financieros del tercer piso",
        "priority": "medium",
    },
    {
        "external_id": "33333333-3333-4333-a333-333333333333",
        "type": "academic",
        "requester_name": "Laura Gómez",
        "email": "laura.gomez@institucion.edu.co",
        "description": "ServiceRequest de corrección de notas del segundo semestre según acta adjunta",
        "priority": "high",
    },
    {
        "external_id": "44444444-4444-4444-a444-444444444444",
        "type": "administrative",
        "requester_name": "Juan Rodríguez",
        "email": "juan.rodriguez@institucion.edu.co",
        "description": "ServiceRequest de paz y salvo para trámite de grado, requiere respuesta urgente",
        "priority": "low",
    },
    {
        "external_id": "55555555-5555-4555-a555-555555555555",
        "type": "technical_support",
        "requester_name": "María López",
        "email": "maria.lopez@institucion.edu.co",
        "description": "El computador del laboratorio 3 no enciende desde el martes en la tarde",
        "priority": "medium",
    },
    # Intentionally invalid request to test 4xx error handling
    {
        "external_id": "66666666-6666-4666-a666-666666666666",
        "type": "tipo_invalido",          # non-existent catalog value
        "requester_name": "Test Error",
        "email": "no-es-email",          # invalid email
        "description": "Error test",
        "priority": "urgente",            # non-existent priority
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


def post_con_retry(
    url: str,
    payload: dict,
    identificador: str,
) -> Optional[dict]:
    last_status: Optional[int] = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        start = time.perf_counter()
        status_code: Optional[int] = None

        try:
            status_code, body = http_post(url, payload, TIMEOUT_S, identificador)
            duration = int((time.perf_counter() - start) * 1000)

            if status_code in (200, 201):
                log.info(
                    "ServiceRequest creada exitosamente",
                    extra={
                        "external_id": identificador,
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
                    "Error definitivo (4xx), no se reintentará",
                    extra={
                        "external_id": identificador,
                        "attempt": attempt,
                        "status_code": status_code,
                        "error": body.get("detail", "Error de cliente"),
                        "method": "POST",
                        "endpoint": url,
                    },
                )
                return None

            # Error 5xx → temporal, reintentar
            log.warning(
                "Temporary error (5xx), retrying",
                extra={
                    "external_id": identificador,
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "status_code": status_code,
                    "error": body.get("detail", "Error de servidor"),
                },
            )

        except (httpx.RequestError, TimeoutError, OSError) as exc:
            duration = int((time.perf_counter() - start) * 1000)
            log.warning(
                "Connection error, retrying",
                extra={
                    "external_id": identificador,
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
                f"Esperando {delay:.1f}s antes del siguiente intento",
                extra={
                    "external_id": identificador,
                    "attempt": attempt,
                },
            )
            time.sleep(delay)

    log.error(
        "Se agotaron los reintentos",
        extra={
            "external_id": identificador,
            "max_attempts": MAX_ATTEMPTS,
            "last_status_code": last_status,
        },
    )
    return None


# ── Main flow ───────────────────────────────────────────────────────────

def esperar_backend() -> None:
    """Active wait until backend responds on /health."""
    health_url = f"{API_BASE_URL.replace('/api/v1', '')}/health"
    log.info("Esperando que el backend esté disponible", extra={"endpoint": health_url})

    for attempt in range(1, 31):
        try:
            status_code, _ = http_get(health_url, timeout=3.0)
            if status_code == 200:
                log.info("Backend disponible", extra={"attempt": attempt})
                return
        except Exception:
            pass

        log.info(
            "Backend aún no disponible, reintentando...",
            extra={"attempt": attempt},
        )
        time.sleep(3)

    raise RuntimeError("El backend no respondió después de 90 segundos")


def consultar_status(request_id: str) -> Optional[dict]:
    url = f"{API_BASE_URL}/requests/{request_id}"
    try:
        status_code, body = http_get(url, timeout=TIMEOUT_S, correlation_id=request_id)
        if status_code == 200:
            log.info(
                "Status consultado",
                extra={
                    "request_id": request_id,
                    "status_code": status_code,
                    "method": "GET",
                    "endpoint": url,
                },
            )
            return body
        log.warning(
            "No se pudo consultar el status",
            extra={"request_id": request_id, "status_code": status_code},
        )
    except Exception as exc:
        log.error(
            "Error al consultar status",
            extra={"request_id": request_id, "error": str(exc)},
        )
    return None


def main() -> None:
    log.info("Iniciando consumidor de requests")
    time.sleep(STARTUP_WAIT_S)
    esperar_backend()

    url_crear = f"{API_BASE_URL}/requests"
    resultados: list[dict] = []

    # ── Phase 1: create all requests ──────────────────────────────────
    log.info(f"Iniciando creación de {len(SOLICITUDES)} requests")

    for request in SOLICITUDES:
        ident = request["external_id"]
        log.info("Enviando request", extra={"external_id": ident})
        resultado = post_con_retry(url_crear, request, ident)
        if resultado:
            resultados.append(resultado)

    log.info(
        "Fase de creación completed",
        extra={"creadas": len(resultados), "fallidas": len(SOLICITUDES) - len(resultados)},
    )

    if not resultados:
        log.error("Ninguna solicitud fue creada exitosamente.")
        sys.exit(1)

    # ── Phase 2: check status of created ones ───────────────────────────────
    log.info("Consultando status de requests creadas")
    time.sleep(2)

    for item in resultados:
        status_actual = consultar_status(item["external_id"])
        if status_actual:
            log.info(
                "Resumen de request",
                extra={
                    "request_id": item["external_id"],
                    "external_id": item["external_id"],
                    "status": status_actual["status"],
                    "priority": status_actual["priority"],
                },
            )

    log.info("Consumer successfully completed")


if __name__ == "__main__":
    main()
