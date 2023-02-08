"""
    Support for paginated results using Pydantic
"""
import json
from math import ceil
from typing import Generic, List, TypeVar

from .paginated import Pagination

T = TypeVar("T")


class PaginatedResult(Pagination, Generic[T]):
    """Defines a Paginated result model"""

    page_count: int
    first_page: bool
    previous_page: bool
    next_page: bool
    last_page: bool
    result: List[T]

    @classmethod
    def from_db(
        cls,
        result: List[T],
        page_settings: Pagination | None = None,
        total_count: int = 0,
    ):
        """Returns a paginated result from a database result set"""
        if not page_settings:
            page_settings = Pagination.from_params({})

        last_page_count = total_count / page_settings.per_page

        return cls(
            page=page_settings.page,
            per_page=page_settings.per_page,
            page_count=len(result),
            first_page=(page_settings.page == 1),
            previous_page=(page_settings.page > 1),
            next_page=len(result) <= total_count,
            last_page=page_settings.page >= ceil(last_page_count),
            result=result,
        )

    def to_api(self):
        """Return results as s json to be returned by api calls"""
        return json.loads(self.json())
