import enum
from datetime import datetime
from pydantic import BaseModel


class ModerationRequest(BaseModel):
    message_id: int
    sender_email: str
    subject: str
    size_description: str
    reason: str
    received_date: datetime


class ModerationRequestDetails(BaseModel):
    message_id: int
    message_contents: str
    message_headers: str


class ModerationAction(enum.Enum):
    # NOTE: The values are significant; they correspond to values used by
    # Mailman to represent these actions.

    # Defer is a no-op. We include it for completeness.
    Defer = 0
    Approve = 1
    Reject = 2
    Discard = 3
