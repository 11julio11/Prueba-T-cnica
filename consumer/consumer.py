"""
Consumidor de la API de solicitudes.
- Envía solicitudes con retry exponencial
- No reintenta errores 4xx (definitivos)
- Sí reintenta errores 5xx y de conexión (temporales)
- Logs estructurados en JSON
"""
import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from typing import Any, Optional


# ── Logging estructurado JSON ─────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    SERVICE = "solicitudes-consumer"

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.SERVICE,
            "message": record.getMessage(),
        }
        for field in (
            "identificador_externo",
            "solicitud_id",
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


# ── Configuración ─────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "5"))
BASE_DELAY_S = float(os.getenv("BASE_DELAY_S", "1.0"))
MAX_DELAY_S = float(os.getenv("MAX_DELAY_S", "30.0"))
TIMEOUT_S = float(os.getenv("TIMEOUT_S", "10.0"))
STARTUP_WAIT_S = float(os.getenv("STARTUP_WAIT_S", "5.0"))


# ── Solicitudes de ejemplo ────────────────────────────────────────────────────

SOLICITUDES: list[dict] = [
    {
        "identificador_externo": "CONS-001",
        "tipo": "soporte_tecnico",
        "nombre_solicitante": "Ana Martínez",
        "correo": "ana.martinez@institucion.edu.co",
        "descripcion": "No puedo acceder al sistema de notas desde ayer en la mañana",
        "prioridad": "alta",
    },
    {
        "identificador_externo": "CONS-002",
        "tipo": "acceso_plataforma",
        "nombre_solicitante": "Carlos Pérez",
        "correo": "carlos.perez@institucion.edu.co",
        "descripcion": "Necesito acceso al módulo de reportes financieros del tercer piso",
        "prioridad": "media",
    },
    {
        "identificador_externo": "CONS-003",
        "tipo": "academica",
        "nombre_solicitante": "Laura Gómez",
        "correo": "laura.gomez@institucion.edu.co",
        "descripcion": "Solicitud de corrección de notas del segundo semestre según acta adjunta",
        "prioridad": "alta",
    },
    {
        "identificador_externo": "CONS-004",
        "tipo": "administrativa",
        "nombre_solicitante": "Juan Rodríguez",
        "correo": "juan.rodriguez@institucion.edu.co",
        "descripcion": "Solicitud de paz y salvo para trámite de grado, requiere respuesta urgente",
        "prioridad": "baja",
    },
    {
        "identificador_externo": "CONS-005",
        "tipo": "soporte_tecnico",
        "nombre_solicitante": "María López",
        "correo": "maria.lopez@institucion.edu.co",
        "descripcion": "El computador del laboratorio 3 no enciende desde el martes en la tarde",
        "prioridad": "media",
    },
    # Solicitud intencionalmente inválida para probar manejo de errores 4xx
    {
        "identificador_externo": "CONS-ERR",
        "tipo": "tipo_invalido",          # valor de catálogo inexistente
        "nombre_solicitante": "Test Error",
        "correo": "no-es-correo",          # correo inválido
        "descripcion": "Prueba de error",
        "prioridad": "urgente",            # prioridad inexistente
    },
]


# ── HTTP simple sin dependencias externas ─────────────────────────────────────

import urllib.request
import urllib.error


def http_post(url: str, payload: dict, timeout: float) -> tuple[int, dict]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            duration = int((time.perf_counter() - start) * 1000)
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8")) if e.fp else {}
        return e.code, body


def http_get(url: str, timeout: float) -> tuple[int, dict]:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8")) if e.fp else {}
        return e.code, body


# ── Lógica de retry ───────────────────────────────────────────────────────────

def _is_retryable(status_code: Optional[int]) -> bool:
    """5xx y None (error de conexión) son temporales → reintentar."""
    if status_code is None:
        return True
    return status_code >= 500


def _backoff_delay(attempt: int) -> float:
    """Delay exponencial con jitter: min(base * 2^attempt + jitter, max)."""
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
            status_code, body = http_post(url, payload, TIMEOUT_S)
            duration = int((time.perf_counter() - start) * 1000)

            if status_code in (200, 201):
                log.info(
                    "Solicitud creada exitosamente",
                    extra={
                        "identificador_externo": identificador,
                        "solicitud_id": body.get("id"),
                        "attempt": attempt,
                        "status_code": status_code,
                        "duration_ms": duration,
                        "method": "POST",
                        "endpoint": url,
                    },
                )
                return body

            # Error 4xx → definitivo, no reintentar
            if 400 <= status_code < 500:
                log.warning(
                    "Error definitivo (4xx), no se reintentará",
                    extra={
                        "identificador_externo": identificador,
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
                "Error temporal (5xx), reintentando",
                extra={
                    "identificador_externo": identificador,
                    "attempt": attempt,
                    "max_attempts": MAX_ATTEMPTS,
                    "status_code": status_code,
                    "error": body.get("detail", "Error de servidor"),
                },
            )

        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            duration = int((time.perf_counter() - start) * 1000)
            log.warning(
                "Error de conexión, reintentando",
                extra={
                    "identificador_externo": identificador,
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
                    "identificador_externo": identificador,
                    "attempt": attempt,
                },
            )
            time.sleep(delay)

    log.error(
        "Se agotaron los reintentos",
        extra={
            "identificador_externo": identificador,
            "max_attempts": MAX_ATTEMPTS,
            "last_status_code": last_status,
        },
    )
    return None


# ── Flujo principal ───────────────────────────────────────────────────────────

def esperar_backend() -> None:
    """Espera activa hasta que el backend responda en /health."""
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


def consultar_estado(solicitud_id: str) -> Optional[dict]:
    url = f"{API_BASE_URL}/solicitudes/{solicitud_id}"
    try:
        status_code, body = http_get(url, timeout=TIMEOUT_S)
        if status_code == 200:
            log.info(
                "Estado consultado",
                extra={
                    "solicitud_id": solicitud_id,
                    "status_code": status_code,
                    "method": "GET",
                    "endpoint": url,
                },
            )
            return body
        log.warning(
            "No se pudo consultar el estado",
            extra={"solicitud_id": solicitud_id, "status_code": status_code},
        )
    except Exception as exc:
        log.error(
            "Error al consultar estado",
            extra={"solicitud_id": solicitud_id, "error": str(exc)},
        )
    return None


def main() -> None:
    log.info("Iniciando consumidor de solicitudes")
    time.sleep(STARTUP_WAIT_S)
    esperar_backend()

    url_crear = f"{API_BASE_URL}/solicitudes"
    resultados: list[dict] = []

    # ── Fase 1: crear todas las solicitudes ──────────────────────────────────
    log.info(f"Iniciando creación de {len(SOLICITUDES)} solicitudes")

    for solicitud in SOLICITUDES:
        ident = solicitud["identificador_externo"]
        log.info("Enviando solicitud", extra={"identificador_externo": ident})
        resultado = post_con_retry(url_crear, solicitud, ident)
        if resultado:
            resultados.append(resultado)

    log.info(
        "Fase de creación completada",
        extra={"creadas": len(resultados), "fallidas": len(SOLICITUDES) - len(resultados)},
    )

    # ── Fase 2: consultar estado de las creadas ───────────────────────────────
    if resultados:
        log.info("Consultando estado de solicitudes creadas")
        time.sleep(2)

        for item in resultados:
            estado_actual = consultar_estado(item["id"])
            if estado_actual:
                log.info(
                    "Resumen de solicitud",
                    extra={
                        "solicitud_id": item["id"],
                        "identificador_externo": item["identificador_externo"],
                        "estado": estado_actual["estado"],
                        "prioridad": estado_actual["prioridad"],
                    },
                )

    log.info("Consumidor finalizado correctamente")


if __name__ == "__main__":
    main()
