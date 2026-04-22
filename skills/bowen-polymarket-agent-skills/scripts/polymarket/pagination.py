"""Async pagination helpers."""

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def paginate(
    fetch_page: Callable[[int, int], Awaitable[list[T]]],
    limit: int = 100,
    max_items: int | None = None,
) -> AsyncIterator[T]:
    """Generic async paginator.

    Args:
        fetch_page: Async function that takes (offset, limit) and returns a page of items
        limit: Number of items per page
        max_items: Maximum total items to fetch (None for unlimited)

    Yields:
        Items from paginated results

    Example:
        >>> async def fetch(offset, limit):
        ...     return await api.get_markets(offset=offset, limit=limit)
        >>> async for market in paginate(fetch, limit=50):
        ...     print(market.question)
    """
    offset = 0
    total_fetched = 0

    while True:
        # Adjust limit for last page if max_items is set
        current_limit = limit
        if max_items is not None:
            remaining = max_items - total_fetched
            if remaining <= 0:
                break
            current_limit = min(limit, remaining)

        page = await fetch_page(offset, current_limit)

        if not page:
            break

        for item in page:
            yield item
            total_fetched += 1

            if max_items is not None and total_fetched >= max_items:
                return

        # If we got fewer items than requested, we've reached the end
        if len(page) < current_limit:
            break

        offset += len(page)


async def collect_pages(
    fetch_page: Callable[[int, int], Awaitable[list[T]]],
    limit: int = 100,
    max_items: int | None = None,
) -> list[T]:
    """Collect all paginated results into a list.

    Args:
        fetch_page: Async function that takes (offset, limit) and returns a page
        limit: Number of items per page
        max_items: Maximum total items to fetch

    Returns:
        List of all items
    """
    items: list[T] = []
    async for item in paginate(fetch_page, limit, max_items):
        items.append(item)
    return items
