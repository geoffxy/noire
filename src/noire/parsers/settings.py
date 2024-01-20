from bs4 import BeautifulSoup
from noire.models.settings import GeneralOptions


def extract_chunk_size_setting(raw_html: str) -> int:
    soup = BeautifulSoup(raw_html, "html.parser")
    input_tag = soup.find("input", {"name": "admin_member_chunksize"})
    return int(input_tag["value"])  # type: ignore


def extract_general_options(raw_html: str) -> GeneralOptions:
    soup = BeautifulSoup(raw_html, "html.parser")
    raw_values = {}
    for field, field_type in GeneralOptions.model_fields.items():
        if field_type.annotation is int or field_type.annotation is str:
            tag = soup.find(None, {"name": field})
            if tag.name == "input":  # type: ignore
                value = tag["value"]  # type: ignore
            elif tag.name == "textarea":  # type: ignore
                value = tag.text  # type: ignore
            else:
                raise NotImplementedError(
                    f"Unsupported tag type {tag.name} for field {field}"  # type: ignore
                )
            if field_type.annotation is type(int):
                value = int(value)
            raw_values[field] = value

        elif field_type.annotation is bool:
            inputs = soup.find_all("input", {"name": field})
            value = None
            for tag in inputs:
                if "checked" in tag.attrs:  # type: ignore
                    value = tag["value"] == "1"  # type: ignore
                    break
            if value is None:
                raise RuntimeError(f"Unset boolean option {field}")
            raw_values[field] = value

        else:
            raise NotImplementedError(f"Unsupported field {field} {field_type}")

    return GeneralOptions(**raw_values)  # type: ignore
