from typing import List, Optional


class MemberError:
    def __init__(self, email: str, error_reason: Optional[str]) -> None:
        self.email = email
        self.error_reason = error_reason

    def __repr__(self) -> str:
        return "".join(["(", self.email, ", reason=", str(self.error_reason), ")"])


class BulkAddResults:
    def __init__(self, added: List[str], errors: List[MemberError]) -> None:
        self.added = added
        self.errors = errors

    def __repr__(self) -> str:
        added = "\n    ".join(self.added)
        errors = "\n    ".join(map(repr, self.errors))
        return "\n".join(
            ["BulkAddResults", "  Added:", "    " + added, "  Errors:", "    " + errors]
        )


class BulkRemoveResults:
    def __init__(self, removed: List[str]) -> None:
        self.removed = removed

    def __repr__(self) -> str:
        removed = "\n    ".join(self.removed)
        return "\n".join(["BulkRemoveResults", "  Removed:", "    " + removed])
