import pytest

from common.pagination import Paginator


class TestPaginator:
    @pytest.mark.parametrize(
        ("current", "per_page", "expected"),
        [
            (1, 25, 0),
            (2, 25, 25),
            (4, 15, 45),
        ],
    )
    def test_offset(self, current, per_page, expected):
        paginator = Paginator(total=100, current=current, per_page=per_page)
        assert paginator.offset == expected

    @pytest.mark.parametrize(
        ("current", "expected"),
        [
            (1, True),
            (5, True),
            (10, False),
            (11, False),
        ],
    )
    def test_has_next(self, current, expected):
        paginator = Paginator(total=100, current=current, per_page=10)
        assert paginator.has_next == expected

    @pytest.mark.parametrize(
        ("current", "expected"),
        [
            (1, False),
            (5, True),
            (10, True),
        ],
    )
    def test_has_previous(self, current, expected):
        paginator = Paginator(total=100, current=current, per_page=10)
        assert paginator.has_previous == expected

    @pytest.mark.parametrize(
        ("current", "expected"),
        [
            (1, list(range(1, 6))),
            (5, list(range(1, 10))),
            (9, list(range(5, 11))),
        ],
    )
    def test_iteration(self, current, expected):
        paginator = Paginator(total=100, current=current, per_page=10)
        assert [i for i in paginator] == expected

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
    def test_pages(self, total, per_page, expected):
        paginator = Paginator(total=total, current=1, per_page=per_page)
        assert paginator.pages == len(paginator) == expected

    @pytest.mark.parametrize(
        ("total", "per_page", "expected"),
        [
            (100, 10, True),
            (5, 4, True),
            (5, 5, False),
            (5, 6, False),
        ],
    )
    def test_bool(self, total, per_page, expected):
        paginator = Paginator(total=total, current=1, per_page=per_page)
        assert bool(paginator) is expected
