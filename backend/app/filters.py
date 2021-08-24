from typing import Union
from urllib.parse import parse_qs, urlencode, urlparse

from flask.app import Flask


def to_page(url: str, page_number: Union[str, int]) -> str:
    parsed = urlparse(url)

    params = parse_qs(parsed.query)
    params["page"] = [str(page_number)]
    query = urlencode(params, doseq=True)

    return parsed._replace(query=query).geturl()


def init_app(app: Flask):
    app.jinja_env.filters["to_page"] = to_page
