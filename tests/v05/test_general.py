"""
General tests.
"""

import re

import numpy as np
import pytest
from pydantic import ValidationError

from ome_zarr_models._v05.labels import Labels, LabelsAttrs
from tests.v05.conftest import json_to_zarr_group


def test_no_ome_version_fails() -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_no_version_example.json")
    zarr_group.create_dataset("cell_space_segmentation", shape=(1, 1), dtype=np.int64)
    print(print(LabelsAttrs.model_json_schema()))
    with pytest.raises(ValidationError, match=re.escape("attributes.ome.version")):
        Labels.from_zarr(zarr_group)
