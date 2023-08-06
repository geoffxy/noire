from bs4 import BeautifulSoup
from typing import List


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
