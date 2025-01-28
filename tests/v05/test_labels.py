import re

import numpy as np
import pytest

from ome_zarr_models._v05.labels import Labels, LabelsAttrs
from tests.v05.conftest import json_to_zarr_group


def test_labels() -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_example.json")
    zarr_group.create_dataset("cell_space_segmentation", shape=(1, 1), dtype=np.int64)
    ome_group = Labels.from_zarr(zarr_group)
    assert ome_group.attributes.ome == LabelsAttrs(
        labels=["cell_space_segmentation"], version="0.5"
    )


def test_labels_invalid_dtype() -> None:
    """
    Check that an invalid data type raises an error.
    """
    zarr_group = json_to_zarr_group(json_fname="labels_example.json")
    zarr_group.create_dataset("cell_space_segmentation", shape=(1, 1), dtype=np.float64)
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Data type of labels at 'cell_space_segmentation' is not valid. "
            "Got float64, should be one of "
            "['uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32', 'uint64', 'int64']"
        ),
    ):
        Labels.from_zarr(zarr_group)
