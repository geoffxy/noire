from typing import Optional
from pydantic import BaseModel


class GeneralOptions(BaseModel):
    """
    Settings found on Mailman's "General Options" page.

    See Mailman for descriptions of the options.
    https://www.gnu.org/software/mailman/mailman-admin/node13.html
    """

    # Notifications
    send_reminders: bool
    welcome_msg: str
    send_welcome_msg: bool
    goodbye_msg: str
    send_goodbye_msg: bool
    admin_immed_notify: bool
    admin_notify_mchanges: bool
    respond_to_post_requests: bool

    # Additional settings
    admin_member_chunksize: int


class GeneralOptionsChanges(BaseModel):
    """
    Used to make changes to Mailman's "General Options". Set a value to indicate
    that it should be modified. This allows for setting changes without fetching
    all the existing options.
    """

    send_reminders: Optional[bool] = None
    welcome_msg: Optional[str] = None
    send_welcome_msg: Optional[bool] = None
    goodbye_msg: Optional[str] = None
    send_goodbye_msg: Optional[bool] = None
    admin_immed_notify: Optional[bool] = None
    admin_notify_mchanges: Optional[bool] = None
    respond_to_post_requests: Optional[bool] = None

    admin_member_chunksize: Optional[int] = None
