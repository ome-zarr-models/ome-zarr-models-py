"""
General tests.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ome_zarr_models.v05.image import Image
from tests.v05.conftest import json_to_zarr_group

if TYPE_CHECKING:
    from zarr.abc.store import Store


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
