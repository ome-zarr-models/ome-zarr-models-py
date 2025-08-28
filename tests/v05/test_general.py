"""
General tests.
"""

import re

import numpy as np
import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

from ome_zarr_models.v05.labels import Labels
from tests.conftest import UnlistableStore
from tests.v05.conftest import json_to_zarr_group


def test_no_ome_version_fails(store: Store) -> None:
    if isinstance(store, UnlistableStore):
        pytest.xfail("Labels does not work on unlistable stores")
    zarr_group = json_to_zarr_group(
        json_fname="labels_no_version_example.json", store=store
    )
    zarr_group.create_array("cell_space_segmentation", shape=(1, 1), dtype=np.int64)
    with pytest.raises(ValidationError, match=re.escape("attributes.ome.version")):
        Labels.from_zarr(zarr_group)
