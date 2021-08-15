from flask import url_for


def full_url(url: str) -> str:
    return "http://localhost" + url


def full_url_for(endpoint: str, **kwargs) -> str:
    return "http://localhost" + url_for(endpoint, **kwargs)
