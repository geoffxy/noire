from typing import List, Optional, Dict
from urllib.parse import quote
from pydantic import BaseModel


class MemberError(BaseModel):
    email: str
    error_reason: Optional[str]


class BulkAddResults(BaseModel):
    added: List[str]
    errors: List[MemberError]


class BulkRemoveResults(BaseModel):
    removed: List[str]


class MemberSettings(BaseModel):
    # The member's email address.
    email: str

    # The user's personal moderation flag. If this is set, postings from them
    # will be moderated, otherwise they will be approved.
    moderated: bool
    # Is the member's address concealed on the list of subscribers?
    hide: bool
    # Is delivery to the member disabled?
    no_mail: bool
    # Does the member get acknowledgements of their posts?
    ack: bool
    # Does the member want to avoid copies of their own postings?
    not_me_too: bool
    # Does the member want to avoid duplicates of the same message?
    no_dupes: bool
    # Does the member get messages in digests?
    digest: bool
    # If getting digests, does the member get plain text digests?
    plain: bool

    @classmethod
    def from_html_values(
        cls, email: str, setting_enabled: Dict[str, bool]
    ) -> "MemberSettings":
        return MemberSettings(
            email=email,
            moderated=setting_enabled["mod"],
            hide=setting_enabled["hide"],
            no_mail=setting_enabled["nomail"],
            ack=setting_enabled["ack"],
            not_me_too=setting_enabled["notmetoo"],
            no_dupes=setting_enabled["nodupes"],
            digest=setting_enabled["digest"],
            plain=setting_enabled["plain"],
        )

    def to_html_values(self) -> Dict[str, str]:
        email = quote(self.email)
        values = {
            "user": email,
        }
        if self.moderated:
            values[f"{email}_mod"] = "on"
        if self.hide:
            values[f"{email}_hide"] = "on"
        if self.no_mail:
            values[f"{email}_nomail"] = "on"
        if self.ack:
            values[f"{email}_ack"] = "on"
        if self.not_me_too:
            values[f"{email}_notmetoo"] = "on"
        if self.no_dupes:
            values[f"{email}_nodupes"] = "on"
        if self.digest:
            values[f"{email}_digest"] = "on"
        if self.plain:
            values[f"{email}_plain"] = "on"
        return values
