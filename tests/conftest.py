from typing import Any
import requests


def fetch_schemas(*, version: str, schema_name: str, strict: bool) -> dict[str, Any]:
    """
    Get the relaxed and strict schemas for a given version of the spec.
    """
    if strict:
        return requests.get(
            f"https://ngff.openmicroscopy.org/{version}/schemas/strict_{schema_name}.schema",
            verify=False,
        ).json()
    else:
        return requests.get(
            f"https://ngff.openmicroscopy.org/{version}/schemas/{schema_name}.schema",
            verify=False,
        ).json()