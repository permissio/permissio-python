"""
Permissio.io Python SDK

A Python SDK for interacting with the Permissio.io authorization platform.
"""

from permissio.client import Permissio
from permissio.config import ConfigBuilder, PermissioConfig
from permissio.errors import PermissioApiError, PermissioError, PermissioValidationError

__version__ = "0.1.0"
__all__ = [
    "Permissio",
    "PermissioConfig",
    "ConfigBuilder",
    "PermissioError",
    "PermissioApiError",
    "PermissioValidationError",
]
