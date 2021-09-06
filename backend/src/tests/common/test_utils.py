import pytest

from common import utils


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("Hello world", "Hello world"),
        ("<p><strong>Hello</strong> world</p><br>", "Hello world"),
    ],
)
def test_strip_tags(html, expected):
    assert utils.strip_tags(html) == expected
