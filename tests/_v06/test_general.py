"""
General tests.
"""

import re

import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

from ome_zarr_models._v06.image import Image
from tests._v06.conftest import json_to_zarr_group


def test_no_ome_version_fails(store: Store) -> None:
    zarr_group = json_to_zarr_group(
        json_fname="image_no_version_example.json", store=store
    )
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
    )
    zarr_group.create_array("1", shape=(1, 1, 1, 1, 1), dtype="uint8")
    zarr_group.create_array("2", shape=(1, 1, 1, 1, 1), dtype="uint8")
    with pytest.raises(ValidationError, match=re.escape("version")):
        Image.from_zarr(zarr_group)
