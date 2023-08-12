import requests
from typing import List, Optional

from noire.constants import (
    LOG_IN_URL_TEMPLATE,
    GET_MEMBERS_LIST_URL_TEMPLATE,
    MODERATION_REQUESTS_URL_TEMPLATE,
    MODERATION_DETAILS_URL_TEMPLATE,
    ADD_MEMBERS_URL_TEMPLATE,
    REMOVE_MEMBERS_URL_TEMPLATE,
)
from noire.models.membership import BulkAddResults, BulkRemoveResults
from noire.models.moderation import ModerationRequest, ModerationDetails
from noire.parsers.members_list import (
    extract_member_emails,
    extract_add_results,
    extract_remove_results,
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
    def connect(
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
        get_url = GET_MEMBERS_LIST_URL_TEMPLATE.format(
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

    def get_moderation_details(self, message_id: int) -> Optional[ModerationDetails]:
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

    def add_members(self, emails: List[str]) -> BulkAddResults:
        """
        Subscribes the given emails to the list. Returns the emails that were
        successfully subscribed and the emails that failed to be subscribed.
        """
        endpoint = ADD_MEMBERS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "subscribees": "\n".join(emails),
        }
        response = self._session.post(endpoint, payload)
        return extract_add_results(response.content.decode())

    def remove_members(self, emails: List[str]) -> BulkRemoveResults:
        """
        Unsubscribes the given emails from the list. Returns the emails that were
        successfully removed.
        """
        endpoint = REMOVE_MEMBERS_URL_TEMPLATE.format(
            mailman_base_url=self._mailman_base_url, list_name=self._list_name
        )
        payload = {
            "adminpw": self._list_password,
            "unsubscribees": "\n".join(emails),
        }
        response = self._session.post(endpoint, payload)
        return extract_remove_results(response.content.decode())
