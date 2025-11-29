"""
Base API client for the Permis.io SDK.
"""

import time
import logging
from typing import Optional, Dict, Any, TypeVar, Type, List, Union
from urllib.parse import urljoin

import httpx

from permisio.config import PermisConfig
from permisio.errors import (
    PermisApiError,
    PermisNetworkError,
    PermisTimeoutError,
    PermisRateLimitError,
    PermisAuthenticationError,
    PermisPermissionError,
    PermisNotFoundError,
    PermisConflictError,
)

T = TypeVar("T")

logger = logging.getLogger("permisio")


class BaseApiClient:
    """
    Base API client with HTTP utilities, retry logic, and error handling.

    This class provides the foundation for all resource-specific API clients.
    """

    # API URL patterns
    FACTS_API_PREFIX = "/v1/facts"
    SCHEMA_API_PREFIX = "/v1/schema"
    ALLOWED_API_PREFIX = "/v1/allowed"

    def __init__(self, config: PermisConfig) -> None:
        """
        Initialize the base API client.

        Args:
            config: The SDK configuration.
        """
        self.config = config
        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the synchronous HTTP client."""
        if self._client is None:
            if self.config.http_client is not None:
                self._client = self.config.http_client
            else:
                self._client = httpx.Client(
                    timeout=httpx.Timeout(self.config.timeout),
                    headers=self._get_default_headers(),
                )
        return self._client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create the asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self._get_default_headers(),
            )
        return self._async_client

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "permisio-python/0.1.0",
        }
        headers.update(self.config.custom_headers)
        return headers

    def _build_facts_url(self, path: str) -> str:
        """
        Build a Facts API URL.

        Args:
            path: The path after the project/environment segment.

        Returns:
            The full URL.

        Raises:
            ValueError: If project_id or environment_id is not set.
        """
        if not self.config.has_scope():
            raise ValueError("project_id and environment_id are required for this operation")
        
        base_path = f"{self.FACTS_API_PREFIX}/{self.config.project_id}/{self.config.environment_id}"
        full_path = f"{base_path}/{path.lstrip('/')}" if path else base_path
        return urljoin(self.config.api_url + "/", full_path.lstrip("/"))

    def _build_schema_url(self, path: str) -> str:
        """
        Build a Schema API URL.

        Args:
            path: The path after the project/environment segment.

        Returns:
            The full URL.

        Raises:
            ValueError: If project_id or environment_id is not set.
        """
        if not self.config.has_scope():
            raise ValueError("project_id and environment_id are required for this operation")
        
        base_path = f"{self.SCHEMA_API_PREFIX}/{self.config.project_id}/{self.config.environment_id}"
        full_path = f"{base_path}/{path.lstrip('/')}" if path else base_path
        return urljoin(self.config.api_url + "/", full_path.lstrip("/"))

    def _build_allowed_url(self) -> str:
        """
        Build the Allowed (permission check) API URL.

        Returns:
            The full URL.

        Raises:
            ValueError: If project_id or environment_id is not set.
        """
        if not self.config.has_scope():
            raise ValueError("project_id and environment_id are required for this operation")
        
        path = f"{self.ALLOWED_API_PREFIX}/{self.config.project_id}/{self.config.environment_id}"
        return urljoin(self.config.api_url + "/", path.lstrip("/"))

    def _build_url(self, path: str) -> str:
        """
        Build a generic API URL (no project/environment scope).

        Args:
            path: The API path.

        Returns:
            The full URL.
        """
        return urljoin(self.config.api_url + "/", path.lstrip("/"))

    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Handle error responses from the API.

        Args:
            response: The HTTP response.

        Raises:
            PermisApiError: An appropriate error based on the status code.
        """
        status_code = response.status_code
        request_id = response.headers.get("X-Request-ID")

        # Try to parse error body
        try:
            error_body = response.json()
            message = error_body.get("message", error_body.get("error", response.text))
            code = error_body.get("code")
            details = error_body.get("details", {})
        except Exception:
            message = response.text or f"HTTP {status_code} error"
            code = None
            details = {}

        # Raise appropriate error type
        if status_code == 401:
            raise PermisAuthenticationError(message=message, details=details, request_id=request_id)
        elif status_code == 403:
            raise PermisPermissionError(message=message, details=details, request_id=request_id)
        elif status_code == 404:
            raise PermisNotFoundError(message=message, details=details, request_id=request_id)
        elif status_code == 409:
            raise PermisConflictError(message=message, details=details, request_id=request_id)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise PermisRateLimitError(
                message=message, retry_after=retry_after_int, details=details, request_id=request_id
            )
        else:
            raise PermisApiError(
                message=message, status_code=status_code, code=code, details=details, request_id=request_id
            )

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if a request should be retried.

        Args:
            exception: The exception that occurred.
            attempt: The current attempt number (0-indexed).

        Returns:
            True if the request should be retried.
        """
        if attempt >= self.config.retry_attempts:
            return False

        # Retry on network errors
        if isinstance(exception, (PermisNetworkError, PermisTimeoutError)):
            return True

        # Retry on specific API errors
        if isinstance(exception, PermisApiError) and exception.is_retryable:
            return True

        return False

    def _calculate_retry_delay(self, attempt: int, exception: Optional[Exception] = None) -> float:
        """
        Calculate the delay before retrying a request.

        Uses exponential backoff with a base of 1 second.

        Args:
            attempt: The current attempt number (0-indexed).
            exception: The exception that caused the retry (optional).

        Returns:
            The delay in seconds.
        """
        # If rate limited with Retry-After header, use that
        if isinstance(exception, PermisRateLimitError) and exception.retry_after:
            return float(exception.retry_after)

        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        return min(2**attempt, 30)  # Cap at 30 seconds

    def _log_request(self, method: str, url: str, body: Optional[Dict] = None) -> None:
        """Log a request if debug mode is enabled."""
        if self.config.debug:
            logger.debug(f"Request: {method} {url}")
            if body:
                logger.debug(f"Body: {body}")

    def _log_response(self, response: httpx.Response) -> None:
        """Log a response if debug mode is enabled."""
        if self.config.debug:
            logger.debug(f"Response: {response.status_code}")
            try:
                logger.debug(f"Body: {response.json()}")
            except Exception:
                logger.debug(f"Body: {response.text}")

    def request(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make a synchronous HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            url: The full URL.
            json: Request body as JSON.
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            PermisApiError: If the request fails after all retries.
        """
        self._log_request(method, url, json)

        last_exception: Optional[Exception] = None
        for attempt in range(self.config.retry_attempts + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=self._clean_params(params),
                )
                self._log_response(response)

                if response.is_success:
                    return response
                else:
                    self._handle_error_response(response)

            except httpx.TimeoutException as e:
                last_exception = PermisTimeoutError(original_error=e)
            except httpx.NetworkError as e:
                last_exception = PermisNetworkError(f"Network error: {e}", original_error=e)
            except (PermisApiError, PermisNetworkError, PermisTimeoutError) as e:
                last_exception = e

            if last_exception and self._should_retry(last_exception, attempt):
                delay = self._calculate_retry_delay(attempt, last_exception)
                if self.config.debug:
                    logger.debug(f"Retrying in {delay}s (attempt {attempt + 1})")
                time.sleep(delay)
            elif last_exception:
                if self.config.throw_on_error:
                    raise last_exception
                else:
                    # Return a mock response for non-throwing mode
                    return httpx.Response(
                        status_code=getattr(last_exception, "status_code", 500),
                        content=str(last_exception).encode(),
                    )

        # This shouldn't be reached, but just in case
        if last_exception:
            raise last_exception
        raise PermisNetworkError("Request failed with unknown error")

    async def request_async(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make an asynchronous HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            url: The full URL.
            json: Request body as JSON.
            params: Query parameters.

        Returns:
            The HTTP response.

        Raises:
            PermisApiError: If the request fails after all retries.
        """
        import asyncio

        self._log_request(method, url, json)

        last_exception: Optional[Exception] = None
        for attempt in range(self.config.retry_attempts + 1):
            try:
                response = await self.async_client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=self._clean_params(params),
                )
                self._log_response(response)

                if response.is_success:
                    return response
                else:
                    self._handle_error_response(response)

            except httpx.TimeoutException as e:
                last_exception = PermisTimeoutError(original_error=e)
            except httpx.NetworkError as e:
                last_exception = PermisNetworkError(f"Network error: {e}", original_error=e)
            except (PermisApiError, PermisNetworkError, PermisTimeoutError) as e:
                last_exception = e

            if last_exception and self._should_retry(last_exception, attempt):
                delay = self._calculate_retry_delay(attempt, last_exception)
                if self.config.debug:
                    logger.debug(f"Retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
            elif last_exception:
                if self.config.throw_on_error:
                    raise last_exception
                else:
                    return httpx.Response(
                        status_code=getattr(last_exception, "status_code", 500),
                        content=str(last_exception).encode(),
                    )

        if last_exception:
            raise last_exception
        raise PermisNetworkError("Request failed with unknown error")

    def _clean_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Clean query parameters by removing None values.

        Args:
            params: The query parameters.

        Returns:
            The cleaned parameters.
        """
        if params is None:
            return None
        return {k: v for k, v in params.items() if v is not None}

    def get(self, url: str, *, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make a GET request."""
        return self.request("GET", url, params=params)

    def post(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make a POST request."""
        return self.request("POST", url, json=json)

    def put(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make a PUT request."""
        return self.request("PUT", url, json=json)

    def patch(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make a PATCH request."""
        return self.request("PATCH", url, json=json)

    def delete(self, url: str) -> httpx.Response:
        """Make a DELETE request."""
        return self.request("DELETE", url)

    async def get_async(self, url: str, *, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make an async GET request."""
        return await self.request_async("GET", url, params=params)

    async def post_async(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make an async POST request."""
        return await self.request_async("POST", url, json=json)

    async def put_async(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make an async PUT request."""
        return await self.request_async("PUT", url, json=json)

    async def patch_async(self, url: str, *, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        """Make an async PATCH request."""
        return await self.request_async("PATCH", url, json=json)

    async def delete_async(self, url: str) -> httpx.Response:
        """Make an async DELETE request."""
        return await self.request_async("DELETE", url)

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    async def close_async(self) -> None:
        """Close the async HTTP client."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> "BaseApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "BaseApiClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close_async()
