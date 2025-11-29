"""
Error types for the Permis.io SDK.
"""

from typing import Optional, Dict, Any


class PermisError(Exception):
    """
    Base exception for all Permis.io SDK errors.

    Attributes:
        message: Human-readable error message.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class PermisValidationError(PermisError):
    """
    Exception raised for configuration or input validation errors.

    Attributes:
        message: Human-readable error message.
        field: The field that failed validation (optional).
    """

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.field = field


class PermisApiError(PermisError):
    """
    Exception raised for API request errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code from the API response.
        code: Error code from the API response (optional).
        details: Additional error details from the API (optional).
        request_id: Request ID for debugging (optional).
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        self.request_id = request_id

    @property
    def is_not_found(self) -> bool:
        """Check if this is a 404 Not Found error."""
        return self.status_code == 404

    @property
    def is_unauthorized(self) -> bool:
        """Check if this is a 401 Unauthorized error."""
        return self.status_code == 401

    @property
    def is_forbidden(self) -> bool:
        """Check if this is a 403 Forbidden error."""
        return self.status_code == 403

    @property
    def is_bad_request(self) -> bool:
        """Check if this is a 400 Bad Request error."""
        return self.status_code == 400

    @property
    def is_conflict(self) -> bool:
        """Check if this is a 409 Conflict error."""
        return self.status_code == 409

    @property
    def is_server_error(self) -> bool:
        """Check if this is a 5xx Server Error."""
        return 500 <= self.status_code < 600

    @property
    def is_retryable(self) -> bool:
        """Check if this error is potentially retryable."""
        return self.status_code in (429, 500, 502, 503, 504)

    def __str__(self) -> str:
        parts = [f"PermisApiError: {self.message}"]
        parts.append(f"(status_code={self.status_code}")
        if self.code:
            parts.append(f", code={self.code}")
        if self.request_id:
            parts.append(f", request_id={self.request_id}")
        parts.append(")")
        return "".join(parts)

    def __repr__(self) -> str:
        return (
            f"PermisApiError(message={self.message!r}, status_code={self.status_code}, "
            f"code={self.code!r}, details={self.details!r}, request_id={self.request_id!r})"
        )


class PermisNetworkError(PermisError):
    """
    Exception raised for network-related errors.

    Attributes:
        message: Human-readable error message.
        original_error: The original exception that caused this error (optional).
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_error = original_error


class PermisTimeoutError(PermisNetworkError):
    """Exception raised when a request times out."""

    def __init__(self, message: str = "Request timed out", original_error: Optional[Exception] = None) -> None:
        super().__init__(message, original_error)


class PermisRateLimitError(PermisApiError):
    """
    Exception raised when rate limited by the API.

    Attributes:
        retry_after: Seconds to wait before retrying (optional).
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=429, code="rate_limit_exceeded", details=details, request_id=request_id)
        self.retry_after = retry_after


class PermisAuthenticationError(PermisApiError):
    """Exception raised for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=401, code="unauthorized", details=details, request_id=request_id)


class PermisPermissionError(PermisApiError):
    """Exception raised when the API key lacks required permissions."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=403, code="forbidden", details=details, request_id=request_id)


class PermisNotFoundError(PermisApiError):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=404, code="not_found", details=details, request_id=request_id)
        self.resource_type = resource_type
        self.resource_id = resource_id


class PermisConflictError(PermisApiError):
    """Exception raised when there's a resource conflict (e.g., duplicate key)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=409, code="conflict", details=details, request_id=request_id)
