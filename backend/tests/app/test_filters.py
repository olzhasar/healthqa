import pytest

from app.filters import to_page


@pytest.mark.parametrize(
    ("page_number", "url", "expected"),
    [
        (
            1,
            "https://example.com/search/5/?query=12lk&sort=something&page=2",
            "https://example.com/search/5/?query=12lk&sort=something&page=1",
        ),
        (
            5,
            "https://example.com/search/5/?query=12lk&page=3&sort=something",
            "https://example.com/search/5/?query=12lk&page=5&sort=something",
        ),
        (
            9,
            "https://example.com/search/",
            "https://example.com/search/?page=9",
        ),
        (
            9,
            "https://example.com/search/2",
            "https://example.com/search/2?page=9",
        ),
    ],
)
def test_to_page(page_number, url, expected):
    assert to_page(url, page_number) == expected
