from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from noire.models.moderation import ModerationRequest, ModerationRequestDetails


def extract_moderation_requests(raw_html: str) -> List[ModerationRequest]:
    results = []
    soup = BeautifulSoup(raw_html, "html.parser")
    held_messages_by_sender = soup.find_all("table", border="1")

    for sender_group in held_messages_by_sender:
        sender = sender_group.find("strong", string="From:")
        sender_wrap = sender.parent
        sender.decompose()
        sender_email = sender_wrap.contents[0].strip()

        links = sender_group.find_all("a", href=True)
        if len(links) < 2:
            # Unexpected layout.
            continue

        for msg_id_link in links[1:]:
            msg_id = msg_id_link["href"].split("=")[-1]

            message = msg_id_link.find_parent("table")

            subject_tag = message.find("strong", string="Subject:")
            subject = subject_tag.find_next("td").text.strip()

            size_tag = message.find("strong", string="Size:")
            size = size_tag.find_next("td").text.strip()

            reason_tag = message.find("strong", string="Reason:")
            reason = reason_tag.find_next("td").text.strip()

            received_tag = message.find("strong", string="Received:")
            received_date = received_tag.find_next("td").text.strip()
            received_date_ts = datetime.strptime(received_date, "%a %b %d %H:%M:%S %Y")

            results.append(
                ModerationRequest(
                    message_id=int(msg_id),
                    sender_email=sender_email,
                    subject=subject,
                    size_description=size,
                    reason=reason,
                    received_date=received_date_ts,
                )
            )

    return results


def extract_moderation_post_details(
    message_id: int, raw_html: str
) -> Optional[ModerationRequestDetails]:
    soup = BeautifulSoup(raw_html, "html.parser")

    excerpt_heading = soup.find("strong", string="Message Excerpt:")
    if excerpt_heading is None:
        # This indicates that there is no such post (held for moderation).
        return None

    excerpt_wrap = excerpt_heading.parent.parent.find("textarea")  # type: ignore
    message_contents = excerpt_wrap.contents[0].text  # type: ignore

    headers_heading = soup.find("strong", string="Message Headers:")
    assert headers_heading is not None, "Moderation details HTML structure has changed."
    headers_wrap = headers_heading.parent.parent.find("textarea")  # type: ignore
    headers = headers_wrap.contents[0].text  # type: ignore

    return ModerationRequestDetails(
        message_id=message_id,
        message_contents=message_contents,
        message_headers=headers,
    )
