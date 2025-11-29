"""
Configuration types and utilities for the Permis.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import httpx

# Constants
DEFAULT_API_URL = "https://api.permis.io"
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRY_ATTEMPTS = 3
API_KEY_PREFIX = "permis_key_"


@dataclass
class PermisConfig:
    """
    Configuration for the Permis.io SDK.

    Attributes:
        token: API key for authentication (required). Must start with 'permis_key_'.
        api_url: Base URL for the Permis.io API. Defaults to https://api.permis.io.
        project_id: Project identifier. Auto-fetched from API key if not provided.
        environment_id: Environment identifier. Auto-fetched from API key if not provided.
        timeout: Request timeout in seconds. Defaults to 30.
        debug: Enable debug logging. Defaults to False.
        retry_attempts: Number of retry attempts for failed requests. Defaults to 3.
        throw_on_error: Whether to raise exceptions on API errors. Defaults to True.
        custom_headers: Additional headers to include in requests.
        http_client: Optional custom httpx client.
    """

    token: str
    api_url: str = DEFAULT_API_URL
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    timeout: float = DEFAULT_TIMEOUT
    debug: bool = False
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    throw_on_error: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    http_client: Optional[httpx.Client] = None

    def __post_init__(self) -> None:
        """Normalize API URL by removing trailing slash."""
        if self.api_url.endswith("/"):
            self.api_url = self.api_url.rstrip("/")

    def has_scope(self) -> bool:
        """Check if both project_id and environment_id are set."""
        return bool(self.project_id and self.environment_id)

    def update_scope(self, project_id: str, environment_id: str) -> None:
        """Update the project_id and environment_id."""
        self.project_id = project_id
        self.environment_id = environment_id

    def validate(self) -> None:
        """
        Validate the configuration.

        Raises:
            ValueError: If validation fails.
        """
        if not self.token:
            raise ValueError("API token is required")

        if not self.token.startswith(API_KEY_PREFIX):
            raise ValueError(f"Invalid API key format: must start with '{API_KEY_PREFIX}'")

        if not self.api_url:
            raise ValueError("API URL is required")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.retry_attempts < 0:
            raise ValueError("Retry attempts must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "token": self.token,
            "api_url": self.api_url,
            "project_id": self.project_id,
            "environment_id": self.environment_id,
            "timeout": self.timeout,
            "debug": self.debug,
            "retry_attempts": self.retry_attempts,
            "throw_on_error": self.throw_on_error,
            "custom_headers": self.custom_headers,
        }


class ConfigBuilder:
    """
    Builder pattern for creating PermisConfig instances.

    Example:
        config = (
            ConfigBuilder("permis_key_your_api_key_here")
            .with_project_id("project-id")
            .with_environment_id("env-id")
            .with_debug(True)
            .with_timeout(60.0)
            .build()
        )
    """

    def __init__(self, token: str) -> None:
        """
        Initialize the config builder with the API token.

        Args:
            token: The API key for authentication.
        """
        self._token = token
        self._api_url = DEFAULT_API_URL
        self._project_id: Optional[str] = None
        self._environment_id: Optional[str] = None
        self._timeout = DEFAULT_TIMEOUT
        self._debug = False
        self._retry_attempts = DEFAULT_RETRY_ATTEMPTS
        self._throw_on_error = True
        self._custom_headers: Dict[str, str] = {}
        self._http_client: Optional[httpx.Client] = None

    def with_api_url(self, url: str) -> "ConfigBuilder":
        """Set the API URL."""
        self._api_url = url
        return self

    def with_project_id(self, project_id: str) -> "ConfigBuilder":
        """Set the project ID."""
        self._project_id = project_id
        return self

    def with_environment_id(self, environment_id: str) -> "ConfigBuilder":
        """Set the environment ID."""
        self._environment_id = environment_id
        return self

    def with_timeout(self, timeout: float) -> "ConfigBuilder":
        """Set the request timeout in seconds."""
        self._timeout = timeout
        return self

    def with_debug(self, debug: bool) -> "ConfigBuilder":
        """Enable or disable debug logging."""
        self._debug = debug
        return self

    def with_retry_attempts(self, attempts: int) -> "ConfigBuilder":
        """Set the number of retry attempts."""
        self._retry_attempts = attempts
        return self

    def with_throw_on_error(self, throw_on_error: bool) -> "ConfigBuilder":
        """Set whether to raise exceptions on API errors."""
        self._throw_on_error = throw_on_error
        return self

    def with_custom_header(self, key: str, value: str) -> "ConfigBuilder":
        """Add a custom header."""
        self._custom_headers[key] = value
        return self

    def with_custom_headers(self, headers: Dict[str, str]) -> "ConfigBuilder":
        """Add multiple custom headers."""
        self._custom_headers.update(headers)
        return self

    def with_http_client(self, client: httpx.Client) -> "ConfigBuilder":
        """Set a custom HTTP client."""
        self._http_client = client
        return self

    def build(self) -> PermisConfig:
        """
        Build the configuration.

        Returns:
            The built PermisConfig instance.
        """
        return PermisConfig(
            token=self._token,
            api_url=self._api_url,
            project_id=self._project_id,
            environment_id=self._environment_id,
            timeout=self._timeout,
            debug=self._debug,
            retry_attempts=self._retry_attempts,
            throw_on_error=self._throw_on_error,
            custom_headers=self._custom_headers.copy(),
            http_client=self._http_client,
        )

    def build_with_validation(self) -> PermisConfig:
        """
        Build the configuration and validate it.

        Returns:
            The built and validated PermisConfig instance.

        Raises:
            ValueError: If validation fails.
        """
        config = self.build()
        config.validate()
        return config


def resolve_config(config: Any) -> PermisConfig:
    """
    Resolve configuration from various input types.

    Args:
        config: A PermisConfig instance, a dict with configuration values,
                or a string (treated as API token).

    Returns:
        A PermisConfig instance.

    Raises:
        ValueError: If the config type is not recognized.
    """
    if isinstance(config, PermisConfig):
        return config

    if isinstance(config, str):
        return PermisConfig(token=config)

    if isinstance(config, dict):
        return PermisConfig(
            token=config.get("token", ""),
            api_url=config.get("api_url", DEFAULT_API_URL),
            project_id=config.get("project_id"),
            environment_id=config.get("environment_id"),
            timeout=config.get("timeout", DEFAULT_TIMEOUT),
            debug=config.get("debug", False),
            retry_attempts=config.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS),
            throw_on_error=config.get("throw_on_error", True),
            custom_headers=config.get("custom_headers", {}),
        )

    raise ValueError(f"Unsupported config type: {type(config)}")
