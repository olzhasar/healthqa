from typing import cast

from werkzeug.local import LocalProxy

from storage.base import Store, get_store

_store = LocalProxy(get_store)
store = cast(Store, _store)


__all__ = ["store", "Store"]
