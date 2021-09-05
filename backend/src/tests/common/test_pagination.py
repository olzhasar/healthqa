import pytest

from common.pagination import Paginator


def test_objects():
    objects = [1, 2, 3]
    paginator = Paginator(objects=objects, total=100, page=1, per_page=20)
    assert paginator.objects == objects


@pytest.mark.parametrize(
    ("page", "per_page", "expected"),
    [
        (1, 25, 0),
        (2, 25, 25),
        (4, 15, 45),
    ],
)
def test_calc_offset(page, per_page, expected):
    assert Paginator.calc_offset(page, per_page) == expected


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (1, True),
        (5, True),
        (10, False),
        (11, False),
    ],
)
def test_has_next(page, expected):
    paginator = Paginator(objects=[], total=100, page=page, per_page=10)
    assert paginator.has_next == expected


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (1, False),
        (5, True),
        (10, True),
    ],
)
def test_has_previous(page, expected):
    paginator = Paginator(objects=[], total=100, page=page, per_page=10)
    assert paginator.has_previous == expected


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (1, range(1, 6)),
        (5, range(1, 10)),
        (9, range(5, 11)),
    ],
)
def test_page_range(page, expected):
    paginator = Paginator(objects=[], total=100, page=page, per_page=10)
    assert paginator.page_range == expected


@pytest.mark.parametrize(
    ("total", "per_page", "expected"),
    [
        (10, 10, 1),
        (11, 10, 2),
        (9, 10, 1),
        (5, 10, 1),
        (100, 10, 10),
    ],
)
def test_n_pages(total, per_page, expected):
    paginator = Paginator(objects=[], total=total, page=1, per_page=per_page)
    assert paginator.n_pages == len(paginator) == expected


@pytest.mark.parametrize(
    ("total", "per_page", "expected"),
    [
        (100, 10, True),
        (5, 4, True),
        (5, 5, False),
        (5, 6, False),
    ],
)
def test_bool(total, per_page, expected):
    paginator = Paginator(objects=[], total=total, page=1, per_page=per_page)
    assert bool(paginator) is expected
