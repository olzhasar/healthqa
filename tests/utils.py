from flask import url_for


def full_url_for(endpoint: str) -> str:
    return "http://localhost" + url_for(endpoint)
