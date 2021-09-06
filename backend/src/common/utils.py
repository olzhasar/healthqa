from html.parser import HTMLParser
from io import StringIO
from typing import Any


class MLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data: Any) -> None:
        self.text.write(data)

    def get_data(self) -> str:
        return self.text.getvalue()


def strip_tags(html: str) -> str:
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()
