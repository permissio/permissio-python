"""
Common models and utilities for the Permissio.io SDK.
"""

from dataclasses import dataclass, field
from typing import TypeVar, Generic, List, Optional, Dict, Any
from datetime import datetime


T = TypeVar("T")


@dataclass
class Pagination:
    """
    Pagination information for list responses.

    Attributes:
        page: Current page number (1-indexed).
        per_page: Number of items per page.
        total: Total number of items.
        total_pages: Total number of pages.
    """

    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pagination":
        """Create a Pagination from a dictionary."""
        return cls(
            page=data.get("page", 1),
            per_page=data.get("per_page", data.get("perPage", 10)),
            total=data.get("total", data.get("total_count", 0)),
            total_pages=data.get("total_pages", data.get("totalPages", data.get("page_count", 0))),
        )


@dataclass
class PaginatedResponse(Generic[T]):
    """
    Generic paginated response wrapper.

    Attributes:
        data: List of items in the current page.
        pagination: Pagination information.
    """

    data: List[T]
    pagination: Pagination

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_factory: callable) -> "PaginatedResponse[T]":
        """
        Create a PaginatedResponse from a dictionary.

        Args:
            data: The response dictionary.
            item_factory: A callable to create items from dictionaries.

        Returns:
            A PaginatedResponse instance.
        """
        items = [item_factory(item) for item in data.get("data", [])]
        
        # Handle both nested pagination object and flat response with total_count/page_count
        if "pagination" in data:
            pagination = Pagination.from_dict(data.get("pagination", {}))
        else:
            # Flat response format: total_count, page_count at top level
            pagination = Pagination.from_dict(data)
        
        return cls(data=items, pagination=pagination)


@dataclass
class ListParams:
    """
    Common parameters for list operations.

    Attributes:
        page: Page number (1-indexed).
        per_page: Number of items per page.
        search: Search query string.
        sort_by: Field to sort by.
        sort_order: Sort order ('asc' or 'desc').
    """

    page: int = 1
    per_page: int = 10
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to query parameters dictionary."""
        params: Dict[str, Any] = {
            "page": self.page,
            "per_page": self.per_page,
        }
        if self.search:
            params["search"] = self.search
        if self.sort_by:
            params["sort_by"] = self.sort_by
        if self.sort_order:
            params["sort_order"] = self.sort_order
        return params


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Parse a datetime string from ISO format.

    Args:
        value: The datetime string.

    Returns:
        A datetime object or None.
    """
    if value is None:
        return None
    try:
        # Handle various ISO formats
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def format_datetime(value: Optional[datetime]) -> Optional[str]:
    """
    Format a datetime to ISO format string.

    Args:
        value: The datetime object.

    Returns:
        An ISO format string or None.
    """
    if value is None:
        return None
    return value.isoformat()
