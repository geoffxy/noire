from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from noire.models.moderation import ModerationRequest


def extract_moderation_requests(raw_html: str) -> List[ModerationRequest]:
    results = []
    soup = BeautifulSoup(raw_html, "html.parser")
    held_messages = soup.find_all("table", border="1")

    for message in held_messages:
        sender = message.find("strong", string="From:")
        sender_wrap = sender.parent
        sender.decompose()
        sender_email = sender_wrap.contents[0].strip()

        links = message.find_all("a", href=True)
        msg_id_link = links[1]
        msg_id = msg_id_link["href"].split("=")[-1]

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
