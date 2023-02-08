"""Pagination model testing"""
import pytest

from gdcbeutils.models.pagination import Pagination


def test_build_pagination_from_params():
    """It builds  a pagination model from parameters"""

    new_pagination = Pagination.from_params(
        {
            "page": 50,
            "per_page": 500,
        }
    )

    assert new_pagination.page == 50
    assert new_pagination.per_page == 500


def test_empty_params_will_go_to_default():
    """It turns zero or negative pages into page 1"""
    new_pagination = Pagination.from_params()

    assert new_pagination.page == 1
    assert new_pagination.per_page == 100


@pytest.mark.parametrize("page", [0, -1])
def test_will_not_accept_zero_page(page: int):
    """It turns zero or negative pages into page 1"""
    new_pagination = Pagination.from_params(
        {
            "page": page,
        }
    )

    assert new_pagination.page == 1


@pytest.mark.parametrize(
    "page, expected_page",
    [(0.456, 1), (5.28, 5), (5.87, 5)],
)
def test_truncate_floating_page_to_floor_int(page: float, expected_page: int):
    """It turns zero or negative pages into page 1"""
    new_pagination = Pagination.from_params(
        {
            "page": page,
        }
    )

    assert new_pagination.page == expected_page
