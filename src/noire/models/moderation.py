from datetime import datetime


class ModerationRequest:
    def __init__(
        self,
        message_id: int,
        sender_email: str,
        subject: str,
        size_description: str,
        reason: str,
        received_date: datetime,
    ) -> None:
        self.message_id = message_id
        self.sender_email = sender_email
        self.subject = subject
        self.size_description = size_description
        self.reason = reason
        self.received_date = received_date

    def __repr__(self) -> str:
        items = ["{}={}".format(k, v) for k, v in self.__dict__.items()]
        return "{}({})".format(self.__class__.__name__, ", ".join(items))


class ModerationDetails:
    def __init__(self, message_id: int, message_contents: str, headers: str) -> None:
        self.message_id = message_id
        self.message_contents = message_contents
        self.headers = headers
