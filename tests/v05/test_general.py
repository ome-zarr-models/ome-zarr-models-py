"""
General tests.
"""

import re

import numpy as np
import pytest
from pydantic import ValidationError

from ome_zarr_models.v05.labels import Labels
from tests.v05.conftest import json_to_zarr_group


def test_no_ome_version_fails() -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_no_version_example.json")
    zarr_group.create_array("cell_space_segmentation", shape=(1, 1), dtype=np.int64)
    with pytest.raises(ValidationError, match=re.escape("attributes.ome.version")):
        Labels.from_zarr(zarr_group)
