# from gdcbeutils.models.pagination import PaginatedResult
"""Pagination model testing"""
import json

from gdcbeutils.models.pagination import PaginatedResult


def test_can_create_paginated_result_with_default_pagination():
    """
    It can create a paginated result from a resultset
    and without pagination
    """
    mock_result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    result = PaginatedResult.from_db(mock_result)

    assert result.page_count == len(mock_result)
    assert result.next_page is False
    assert result.page == 1
    assert result.previous_page is False
    assert result.first_page is True
    assert result.last_page is True


def test_can_stringify_to_api_return():
    """
    It can stringify the model for API responses
    """
    mock_result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    result = PaginatedResult.from_db(mock_result)

    json.dumps(result.to_api())
