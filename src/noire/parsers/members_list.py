from bs4 import BeautifulSoup
from typing import List

from noire.models.membership import BulkAddResults, MemberError, BulkRemoveResults


def extract_member_emails(raw_html: str) -> List[str]:
    """
    Extracts the member emails that appear on `/mailman/admin/<list name>/members`
    from the raw HTML.
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
                error_emails.append(MemberError(parts[0], parts[1]))
            else:
                error_emails.append(MemberError(parts[0], None))

    return BulkAddResults(success_emails, error_emails)


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

    return BulkRemoveResults(removed)


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
