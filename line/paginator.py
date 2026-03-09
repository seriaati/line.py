from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from linebot.v3 import audience

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


class Paginator(Generic[T], AsyncIterator[T]):
    """A generic paginator for LINE Messaging API responses that follow the page/size/hasNextPage pattern."""

    def __init__(
        self,
        fetcher: Callable[..., Any],
        *,
        items_attr: str,
        page: int = 1,
        size: int = 40,
        **kwargs: Any,
    ) -> None:
        self.fetcher = fetcher
        self.items_attr = items_attr
        self.page = page
        self.size = size
        self.kwargs = kwargs

        self._buffer: list[T] = []
        self._has_next_page = True

    def __aiter__(self) -> Paginator[T]:
        return self

    async def __anext__(self) -> T:
        if not self._buffer and self._has_next_page:
            await self._fetch_next_page()

        if not self._buffer:
            raise StopAsyncIteration

        return self._buffer.pop(0)

    async def _fetch_next_page(self) -> None:
        response = await asyncio.to_thread(
            self.fetcher, page=self.page, size=self.size, **self.kwargs
        )

        items = getattr(response, self.items_attr, None)
        if items:
            self._buffer.extend(items)

        self._has_next_page = getattr(response, "has_next_page", False)
        self.page += 1


class AudienceGroupPaginator(Paginator[audience.AudienceGroup]):
    """A paginator for audience groups."""

    def __init__(self, api: audience.ManageAudience, **kwargs: Any) -> None:
        super().__init__(api.get_audience_groups, items_attr="audience_groups", **kwargs)


class SharedAudienceGroupPaginator(Paginator[audience.AudienceGroup]):
    """A paginator for shared audience groups."""

    def __init__(self, api: audience.ManageAudience, **kwargs: Any) -> None:
        super().__init__(api.get_shared_audience_groups, items_attr="audience_groups", **kwargs)
