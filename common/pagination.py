from typing import Union


class Paginator:
    total: int
    current: int
    pages: int
    limit: int
    offset: int

    def __init__(self, *, total: int, current: Union[str, int], per_page: int):
        self.total = total
        self.current = int(current)
        self.limit = per_page
        self.offset = self.limit * (self.current - 1)
        self.pages = (self.total - 1) // self.limit + 1

    def __len__(self):
        return self.pages

    @property
    def has_next(self) -> bool:
        return self.current < self.pages

    @property
    def has_previous(self) -> bool:
        return self.current > 1

    def __iter__(self):
        low = max(1, self.current - 4)
        high = min(self.pages + 1, self.current + 5)

        for i in range(low, high):
            yield i

    def __bool__(self) -> bool:
        return self.pages > 1
