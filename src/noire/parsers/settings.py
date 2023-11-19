from bs4 import BeautifulSoup


def extract_chunk_size_setting(raw_html: str) -> int:
    soup = BeautifulSoup(raw_html, "html.parser")
    input_tag = soup.find("input", {"name": "admin_member_chunksize"})
    return int(input_tag["value"])  # type: ignore
