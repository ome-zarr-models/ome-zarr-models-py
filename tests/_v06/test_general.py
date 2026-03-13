"""
General tests.
"""

import re

import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

import ome_zarr_models._v06
from ome_zarr_models import open_ome_zarr
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


@pytest.mark.vcr
def test_load_scene() -> None:
    scene = open_ome_zarr(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/test-data/v0.6.dev3/idr0050/4995115_output_to_ms.zarr/"
    )
    assert isinstance(scene, ome_zarr_models._v06.Scene)
