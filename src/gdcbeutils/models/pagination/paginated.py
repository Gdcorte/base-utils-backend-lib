"""
    Support for pagination using Pydantic
"""
from typing import Any, Dict

from pydantic import BaseModel, validator


class Pagination(BaseModel):
    """Defines a pagination model"""

    page: int
    per_page: int

    @classmethod
    def from_params(cls, obj: Dict[str, Any] | None = None):
        """Defines a pagination from default parameters"""
        if not obj:
            obj = {}

        return cls(
            page=obj.get("page", 1),
            per_page=obj.get("per_page", 100),
        )

    @validator("page")
    def must_be_at_least_1(cls, value: int):
        """Page must start at 1"""
        if value <= 0:
            return 1
        return value

    def start_index(self):
        return (self.page - 1) * self.per_page
