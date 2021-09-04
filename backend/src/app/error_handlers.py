from __future__ import annotations

from typing import TYPE_CHECKING

from flask import render_template

from repository.exceptions import NotFoundError

if TYPE_CHECKING:
    from flask import Flask


def handle_404(e):
    return render_template("404.html"), 404


def handle_500(e):
    return render_template("500.html"), 500


def init_app(app: Flask):
    app.register_error_handler(404, handle_404)
    app.register_error_handler(NotFoundError, handle_404)
    app.register_error_handler(500, handle_500)
