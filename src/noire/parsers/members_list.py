from bs4 import BeautifulSoup
from typing import List
from urllib.parse import unquote

from noire.models.membership import (
    BulkAddResults,
    MemberError,
    BulkRemoveResults,
    MemberSettings,
)


def extract_member_emails(raw_html: str) -> List[str]:
    """
    Extracts the member emails that appear on `/mailman/admin/<list name>/members`
    from the raw HTML. Note that this may not be an exhaustive list of members
    because the Mailman view is paginated.
    """
    table_index = 4
    member_emails: List[str] = []

    soup = BeautifulSoup(raw_html, "html.parser")

    # Find all the tables on the page
    tables = soup.find_all("table")

    if table_index >= len(tables):
        return member_emails

    table = tables[table_index]
    rows = table.find_all("tr")

    # Skip the first row since it contains the table headers.
    for row in rows[1:]:
        # Find the first 'a' element to get the email address.
        email_element = row.find("a")
        if email_element:
            email = email_element.text.strip()
            member_emails.append(email)

    return member_emails


def extract_add_results(
    raw_html: str,
) -> BulkAddResults:
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract emails under "Successfully subscribed"
    success_subscribing = soup.find("h5", string="Successfully subscribed:")
    if success_subscribing is not None:
        success_emails = _extract_from_malformed_li(
            success_subscribing.find_next("ul").decode_contents()  # type: ignore
        )
    else:
        success_emails = []

    # Extract emails under "Error subscribing"
    error_subscribing = soup.find("h5", string="Error subscribing:")
    error_emails = []

    if error_subscribing is not None:
        cleaned_errors = _extract_from_malformed_li(
            error_subscribing.find_next("ul").decode_contents()  # type: ignore
        )
        for item in cleaned_errors:
            parts = item.split(" -- ")
            if len(parts) > 1:
                error_emails.append(MemberError(email=parts[0], error_reason=parts[1]))
            else:
                error_emails.append(MemberError(email=parts[0], error_reason=None))

    return BulkAddResults(added=success_emails, errors=error_emails)


def extract_remove_results(raw_html: str) -> BulkRemoveResults:
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract emails under "Successfully unsubscribed"
    success_removed = soup.find("h5", string="Successfully Unsubscribed:")
    if success_removed is not None:
        removed = _extract_from_malformed_li(
            success_removed.find_next("ul").decode_contents()  # type: ignore
        )
    else:
        removed = []

    return BulkRemoveResults(removed=removed)


def extract_member_settings(raw_html: str) -> List[MemberSettings]:
    soup = BeautifulSoup(raw_html, "html.parser")
    member_table = soup.find("table", {"width": "90%", "border": "2"})
    rows = member_table.find_all("tr")  # type: ignore
    if len(rows) < 3:
        # No members found.
        return []

    member_settings: List[MemberSettings] = []
    for row in rows[2:]:
        checkboxes = row.find_all("input", type="CHECKBOX")

        setting_enabled = {}
        emails = []

        for checkbox in checkboxes:
            raw_setting_name = checkbox["name"]
            parts = raw_setting_name.split("_")
            setting_name = parts[-1]
            encoded_email = "_".join(parts[:-1])  # Some emails may contain "_".
            emails.append(unquote(encoded_email))
            setting_enabled[setting_name] = checkbox["value"] == "on"

        # Sanity check.
        if len(emails) == 0 or not all(email == emails[0] for email in emails):
            raise RuntimeError("Unexpected member settings page format.")

        member_settings.append(
            MemberSettings.from_html_values(emails[0], setting_enabled)
        )

    return member_settings


def extract_emails_from_roster(raw_html: str) -> List[str]:
    parsed_emails = []
    soup = BeautifulSoup(raw_html, "html.parser")
    member_lists = soup.find_all("ul")
    for member_list in member_lists:
        email_wraps = member_list.find_all("a")
        for a in email_wraps:
            escaped_email = a.decode_contents()
            email_parts = escaped_email.split(" ")
            if email_parts[1] != "at":
                continue
            parsed_emails.append(f"{email_parts[0]}@{email_parts[2]}")
    return parsed_emails


def _extract_from_malformed_li(raw_content: str) -> List[str]:
    # Mailman's lists are malformed (they are missing </li> tags). This function
    # works around the malformed HTML and extracts the intended list items.
    remove_trailing_li = raw_content.replace("</li>", "")
    items = []
    for piece in remove_trailing_li.split("<li>"):
        clean = piece.strip()
        if len(clean) == 0:
            continue
        items.append(clean)
    return items
