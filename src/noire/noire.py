import requests
from typing import List, Optional

from noire.constants import (
    LOG_IN_URL_TEMPLATE,
    MEMBERS_LIST_URL_TEMPLATE,
    MODERATION_REQUESTS_URL_TEMPLATE,
    MODERATION_DETAILS_URL_TEMPLATE,
    ADD_MEMBERS_URL_TEMPLATE,
    REMOVE_MEMBERS_URL_TEMPLATE,
    SYNC_MEMBERS_URL_TEMPLATE,
    SENDER_PRIVACY_URL_TEMPLATE,
)
from noire.models.membership import BulkAddResults, BulkRemoveResults, MemberSettings
from noire.models.moderation import (
    ModerationRequest,
    ModerationRequestDetails,
    ModerationAction,
)
from noire.parsers.members_list import (
    extract_member_emails,
    extract_add_results,
    extract_remove_results,
    extract_member_settings,
)
from noire.parsers.moderation import (
    extract_moderation_requests,
    extract_moderation_post_details,
)


class Noire:
    """
    Provides programmatic access to Mailman 2 via its web user interface.

    This tool is meant to be a modern successor to "mmblanche".
    """

    @classmethod
    def create_client(
        cls,
        list_name: str,
        list_password: str,
        mailman_base_url: str,
    ) -> "Noire":
        session = requests.Session()
        log_in_data = {
            "adminpw": list_password,
        }
        log_in_url = LOG_IN_URL_TEMPLATE.format(
            list_name=list_name, mailman_base_url=mailman_base_url
        )
        response = session.post(log_in_url, data=log_in_data)
        if response.status_code == 401:
            raise RuntimeError(f"Incorrect password for list {list_name}")
        elif response.status_code != 200:
            raise RuntimeError(
                f"Error authenticating to list {list_name}: {response.status_code}"
            )

        return cls(list_name, mailman_base_url, list_password, session)

    def __init__(
        self,
        list_name: str,
        mailman_base_url: str,
        list_password: str,
        session: requests.Session,
    ) -> None:
        self._list_name = list_name
        self._mailman_base_url = mailman_base_url
        self._list_password = list_password
        self._session = session

    def get_member_emails(self) -> List[str]:
        """
        Retrieves all emails that are subscribed to the list.
        """
        get_url = MEMBERS_LIST_URL_TEMPLATE.format(
            list_name=self._list_name, mailman_base_url=self._mailman_base_url
        )
        response = self._session.get(get_url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Unexpected error when fetching member emails: {response.status_code}"
            )
        # TODO: Handle pagination for large lists.
        return extract_member_emails(response.content.decode())

    def get_moderation_requests(self) -> List[ModerationRequest]:
        """
        Retrieves moderation requests for the list (i.e., emails sent to the
        list that are held for moderation).
        """
        get_url = MODERATION_REQUESTS_URL_TEMPLATE.format(
            list_name=self._list_name, mailman_base_url=self._mailman_base_url
        )
        response = self._session.get(get_url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Unexpected error when fetching moderation requests: {response.status_code}"
            )
        return extract_moderation_requests(response.content.decode())

    def get_moderation_details(
        self, message_id: int
    ) -> Optional[ModerationRequestDetails]:
        """
        Retrieves details about a message held for moderation (e.g., the
        message's contents).
        """
        get_url = MODERATION_DETAILS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url,
            list_name=self._list_name,
            message_id=message_id,
        )
        response = self._session.get(get_url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Unexpected error when fetching moderation details for {message_id}: {response.status_code}"
            )
        return extract_moderation_post_details(message_id, response.content.decode())

    def apply_moderation_action(
        self,
        message_id: int,
        action: ModerationAction,
        rejection_message: Optional[str] = None,
        preserve_message_for_admin: bool = False,
        forward_message_to_list_owner: bool = False,
    ) -> bool:
        """
        Applies a moderation action to a message (defer, reject, approve,
        discard). This method returns true if the moderation action request was
        successfully submitted. The `message_id` should correspond to a message
        ID retrieved from `get_moderation_requests()`.

        If a message is rejected, Mailman will send a rejection reason to the
        sender. You can customize this reason with `rejection_message`. If you
        do not set a rejection message, Mailman will use a default message.
        """

        endpoint = MODERATION_REQUESTS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            message_id: action.value,
        }
        if action == ModerationAction.Reject and rejection_message is not None:
            payload[f"comment-{message_id}"] = rejection_message
        if preserve_message_for_admin:
            payload[f"preserve-{message_id}"] = "on"
        if forward_message_to_list_owner:
            payload[f"forward-{message_id}"] = "on"
        response = self._session.post(endpoint, payload)
        return response.status_code == 200

    def add_members(
        self,
        emails: List[str],
        send_welcome_message: bool = False,
        send_owner_notifications: bool = False,
    ) -> BulkAddResults:
        """
        Subscribes the given emails to the list. Returns the emails that were
        successfully subscribed and the emails that failed to be subscribed.

        Optional arguments:
        - send_welcome_message:      Set to notify the new member that they were
                                     added.
        - send_owner_notifications:  Send an email to the list owner about the new
                                     members.
        """
        endpoint = ADD_MEMBERS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "subscribees": "\n".join(emails),
            "subscribe_or_invite": 0,  # 0 indicates subscribe.
            "send_welcome_msg_to_this_batch": 1 if send_welcome_message else 0,
            "send_notifications_to_list_owner": 1 if send_owner_notifications else 0,
        }
        response = self._session.post(endpoint, payload)
        return extract_add_results(response.content.decode())

    def remove_members(
        self,
        emails: List[str],
        send_unsubscribe_message: bool = False,
        send_owner_notifications: bool = False,
    ) -> BulkRemoveResults:
        """
        Unsubscribes the given emails from the list. Returns the emails that were
        successfully removed.

        Optional arguments:
        - send_unsubscribe_message: Set to notify the member that they were removed.
        - send_owner_notifications: Send an email to the list owner about the removed
                                    members.
        """
        endpoint = REMOVE_MEMBERS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "unsubscribees": "\n".join(emails),
            "send_unsub_ack_to_this_batch": 1 if send_unsubscribe_message else 0,
            "send_unsub_notifications_to_list_owner": 1
            if send_owner_notifications
            else 0,
        }
        response = self._session.post(endpoint, payload)
        return extract_remove_results(response.content.decode())

    def sync_members(self, emails: List[str]) -> bool:
        """
        Synchronizes the member list with the provided list of emails.

        Mailman will (i) remove subscribers that are currently subscribed but
        not in `emails`, and (ii) will subscribe emails that are in `emails` but
        are not currently subscribed.
        """
        endpoint = SYNC_MEMBERS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "memberlist": "\n".join(emails),
        }
        response = self._session.post(endpoint, payload)
        return response.status_code == 200

    def bulk_set_moderation_flag(self, should_moderate: bool) -> bool:
        """
        Use this to set all members' "moderation bit".

        If `should_moderate` is set to `True`, all list members will have their
        posts held for moderation. If it is set to False, everyone is able to
        post without their email being held for moderation.
        """
        endpoint = MEMBERS_LIST_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "allmodbit_val": 1 if should_moderate else 0,
            "allmodbit_btn": "Set",
            "adminpw": self._list_password,
        }
        response = self._session.post(endpoint, payload)
        return response.status_code == 200

    def get_member_subscription_settings(self, email: str) -> Optional[MemberSettings]:
        """
        Retrieves a member's subscription settings. If the provided email is not
        subscribed to this list, this method will return `None`.
        """
        endpoint = MEMBERS_LIST_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "findmember": email,  # N.B. Does not need to be URL-encoded.
            "findmember_btn": "Search...",
            "adminpw": self._list_password,
        }
        response = self._session.post(endpoint, payload)
        if response.status_code != 200:
            raise RuntimeError(
                f"Unexpected error when fetching member settings for {email}: {response.status_code}"
            )
        settings = extract_member_settings(response.content.decode())
        for setting in settings:
            if setting.email == email:
                return setting
        # Member not found.
        return None

    def set_member_subscription_settings(self, settings: List[MemberSettings]) -> bool:
        """
        Updates members' subscription settings to the provided settings. Note
        that you can update multiple members' settings at once with this call.
        """
        if len(settings) == 0:
            return True

        endpoint = MEMBERS_LIST_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        # We use a list with tuples here because the payload can have duplicate
        # keys (expected by Mailman).
        payload = [
            ("setmemberopts_btn", "Submit Your Changes"),
            ("adminpw", self._list_password),
        ]
        for setting in settings:
            for k, v in setting.to_html_values().items():
                payload.append((k, v))
        response = self._session.post(endpoint, payload)
        return response.status_code == 200

    def set_accept_these_nonmembers(self, emails: List[str]) -> bool:
        """
        Sets the "accept_these_nonmembers" setting with the provided emails. The
        list will accept messages sent from those email addresses without
        holding them for moderation (as long as those members are also not
        subscribed to the list).
        """
        if len(emails) == 0:
            return True

        endpoint = SENDER_PRIVACY_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "accept_these_nonmembers": "\n".join(emails),
        }
        response = self._session.post(endpoint, payload)
        return response.status_code == 200
