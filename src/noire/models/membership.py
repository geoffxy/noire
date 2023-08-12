from typing import List


class BulkAddResults:
    pass


class BulkRemoveResults:
    def __init__(self, removed: List[str]) -> None:
        self.removed = removed
