from functools import partial

from flask import url_for

full_url_for = partial(url_for, _external=True)
