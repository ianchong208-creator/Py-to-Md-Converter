#!/usr/bin/env python3
"""
A complex example demonstrating advanced Python features.
"""

import functools
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

# Third-party imports (simulated)
# import numpy as np
# import requests

# Local imports (simulated)
# from utils.helpers import validate_input
# from config.settings import APP_CONFIG

# Constants
API_BASE_URL = "https://api.example.com/v1"
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0

# Global variables
_session_cache = {}
_request_count = 0


def retry_on_failure(max_retries: int = 3):
    """Decorator to retry function calls on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
            raise last_exception
        return wrapper
    return decorator


def validate_input(func: Callable) -> Callable:
    """Decorator to validate input parameters."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Simplified validation
        if not args:
            raise ValueError("No arguments provided")
        return func(*args, **kwargs)
    return wrapper


@dataclass
class APIResponse:
    """Data class representing an API response."""
    status_code: int
    data: Dict
    headers: Optional[Dict] = None

    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300


class BaseAPIClient(ABC):
    """Abstract base class for API clients."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self._session = None

    @abstractmethod
    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """Make a GET request to the specified endpoint."""
        pass

    @abstractmethod
    def post(self, endpoint: str, data: Dict) -> APIResponse:
        """Make a POST request to the specified endpoint."""
        pass


class APIClient(BaseAPIClient):
    """Concrete implementation of an API client."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @retry_on_failure(max_retries=MAX_RETRIES)
    @validate_input
    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """Make a GET request to the specified endpoint with retry logic."""
        # Simulated implementation
        self._session_cache[endpoint] = self._session_cache.get(endpoint, 0) + 1
        return APIResponse(
            status_code=200,
            data={"endpoint": endpoint, "params": params or {}},
            headers=self._headers
        )

    @retry_on_failure(max_retries=MAX_RETRIES)
    def post(self, endpoint: str, data: Dict) -> APIResponse:
        """Make a POST request to the specified endpoint."""
        # Simulated implementation
        return APIResponse(
            status_code=201,
            data={"endpoint": endpoint, "data": data},
            headers=self._headers
        )


def process_api_response(response: APIResponse) -> Dict:
    """Process an API response and extract relevant data."""
    if not response.is_success():
        raise ValueError(f"API request failed with status {response.status_code}")

    # Process the response data
    processed = {
        "status": "success",
        "data": response.data,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

    return processed


def main() -> None:
    """Main entry point demonstrating the API client usage."""
    client = APIClient(
        base_url=API_BASE_URL,
        api_key="demo-key-12345",
        timeout=DEFAULT_TIMEOUT
    )

    # Make a GET request
    response = client.get("/users", params={"limit": 10})
    print(f"GET request status: {response.status_code}")

    # Process the response
    try:
        processed_data = process_api_response(response)
        print(f"Processed data: {json.dumps(processed_data, indent=2)}")
    except ValueError as e:
        print(f"Error processing response: {e}")

    # Make a POST request
    post_response = client.post("/users", {"name": "John Doe", "email": "john@example.com"})
    print(f"POST request status: {post_response.status_code}")


if __name__ == "__main__":
    main()