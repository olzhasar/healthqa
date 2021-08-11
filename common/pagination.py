from flask import current_app, request


class Paginator:
    n: int
    current: int
    per_page: int
    pages: int
    limit: int
    offset: int

    def __init__(self, n: int):
        self.n = n
        self.per_page = current_app.config["PAGINATION"]
        self.current = int(request.args.get("page", 1))
        self.limit = self.per_page * self.current
        self.offset = self.per_page * (self.current - 1)
        self.pages = (self.n - 1) // self.per_page + 1

    def __len__(self):
        return self.pages

    @property
    def has_next(self) -> bool:
        return self.current < self.pages

    @property
    def has_previous(self) -> bool:
        return self.current > 1

    def __iter__(self):
        for i in range(1, self.pages + 1):
            yield i

    def __bool__(self) -> bool:
        return self.pages > 1
