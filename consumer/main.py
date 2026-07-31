import os
import requests
import structlog
import uuid
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

API_URL = os.getenv("API_URL", "http://api:8000")
RETRIES = int(os.getenv("CONSUMER_RETRIES", "3"))
TIMEOUT = int(os.getenv("CONSUMER_TIMEOUT", "5"))

class TransientError(Exception):
    """Exception raised for 5xx errors or connection issues, which should be retried."""
    pass

class PermanentError(Exception):
    """Exception raised for 4xx errors, which should NOT be retried."""
    pass

def handle_response(response: requests.Response):
    """Parses response and raises appropriate exceptions for tenacity to handle."""
    if response.status_code >= 500:
        raise TransientError(f"Server error: {response.status_code}")
    elif 400 <= response.status_code < 500:
        raise PermanentError(f"Client error: {response.status_code}")
    return response

@retry(
    retry=retry_if_exception_type(TransientError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(RETRIES),
    reraise=True
)
def send_solicitude(payload: dict):
    """Sends a POST request to create a solicitude with retry logic."""
    url = f"{API_URL}/solicitudes"
    logger.info("Sending request", endpoint=url, method="POST", external_id=payload["external_id"])
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        handle_response(response)
        logger.info("Request successful", status_code=response.status_code, external_id=payload["external_id"])
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Connection error, retrying...", error=str(e), external_id=payload["external_id"])
        raise TransientError(f"Connection error: {e}")

def check_solicitude_status(solicitude_id: int):
    """Fetches the status of a created solicitude."""
    url = f"{API_URL}/solicitudes/{solicitude_id}"
    logger.info("Checking status", endpoint=url, method="GET", solicitude_id=solicitude_id)
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            logger.info("Status retrieved", status_code=200, status=data.get("status"), solicitude_id=solicitude_id)
        else:
            logger.error("Failed to check status", status_code=response.status_code)
    except Exception as e:
        logger.error("Error checking status", error=str(e))

def main():
    logger.info("Starting consumer service")
    
    # Wait a bit for the API to be ready
    time.sleep(10)
    
    # Generate some test data
    test_cases = [
        {
            "desc": "Valid request",
            "payload": {
                "external_id": str(uuid.uuid4()),
                "request_type": "soporte técnico",
                "requester_name": "John Doe",
                "email": "john@example.com",
                "description": "I cannot access my account.",
                "priority": "alta"
            }
        },
        {
            "desc": "Invalid request (Permanent error, 422)",
            "payload": {
                "external_id": str(uuid.uuid4()),
                "request_type": "invalid_type",
                "requester_name": "Jane",
                "email": "not-an-email",
                "description": "short",
                "priority": "baja"
            }
        }
    ]

    for case in test_cases:
        logger.info(f"Running test case: {case['desc']}")
        try:
            result = send_solicitude(case["payload"])
            if result and "id" in result:
                # Later, check its status
                time.sleep(2)
                check_solicitude_status(result["id"])
        except PermanentError as e:
            logger.error("Permanent error encountered, skipping retries", error=str(e))
        except TransientError as e:
            logger.error("Max retries exceeded for transient error", error=str(e))
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
            
    logger.info("Consumer service finished execution")

if __name__ == "__main__":
    main()
