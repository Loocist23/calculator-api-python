"""
HTTP Helper for integration tests
Sends HTTP requests to a test server instance
"""

import time
from typing import Any, Dict

import httpx


async def request(
    server_url: str, path: str, method: str = "GET", timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Send an HTTP request to a test server instance.

    Args:
        server_url: Base URL of the test server (e.g., "http://127.0.0.1:8000")
        path: Path + query string (e.g., "/calculate?operation=add&a=1&b=2")
        method: HTTP method (default: "GET")
        timeout: Request timeout in seconds (default: 5.0)

    Returns:
        Dictionary containing:
        - status: HTTP status code
        - headers: Response headers (lowercase keys)
        - body: Parsed JSON body (or None if empty)
        - duration: Request duration in milliseconds
        - raw_body: Raw response text
    """
    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                f"{server_url}{path}",
                headers={"Content-Type": "application/json"},
            )

            duration = (time.time() - start) * 1000  # Convert to ms

            # Parse body
            raw_body = response.text
            body = None
            if raw_body and raw_body.strip():
                try:
                    body = response.json()
                except Exception:
                    body = None

            # Convert headers to lowercase keys
            headers = {k.lower(): v for k, v in response.headers.items()}

            return {
                "status": response.status_code,
                "headers": headers,
                "body": body,
                "raw_body": raw_body,
                "duration": duration,
            }
    except httpx.TimeoutException:
        return {
            "status": 504,
            "headers": {},
            "body": None,
            "raw_body": "",
            "duration": (time.time() - start) * 1000,
        }
    except Exception as e:
        return {
            "status": 500,
            "headers": {},
            "body": {"error": str(e)},
            "raw_body": str(e),
            "duration": (time.time() - start) * 1000,
        }
