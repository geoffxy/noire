from typing import List, Optional
from pydantic import BaseModel


class MemberError(BaseModel):
    email: str
    error_reason: Optional[str]


class BulkAddResults(BaseModel):
    added: List[str]
    errors: List[MemberError]


class BulkRemoveResults(BaseModel):
    removed: List[str]
