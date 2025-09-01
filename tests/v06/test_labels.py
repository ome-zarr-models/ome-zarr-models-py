import re

import numpy as np
import pytest
from zarr.abc.store import Store

from ome_zarr_models.v05.labels import Labels, LabelsAttrs
from tests.v05.conftest import json_to_zarr_group


def test_labels(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_example.json", store=store)
    image_group = zarr_group.create_group("cell_space_segmentation")
    image_group.attrs.put(
        json_to_zarr_group(
            json_fname="labels_image_example.json", store=store
        ).attrs.asdict()
    )
    image_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype=np.uint64,
        dimension_names=["t", "c", "z", "y", "x"],
    )

    ome_group = Labels.from_zarr(zarr_group)
    assert ome_group.attributes.ome == LabelsAttrs(
        labels=["cell_space_segmentation"], version="0.5"
    )


def test_labels_no_images(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_example.json", store=store)
    with pytest.raises(
        ValueError,
        match="Label path 'cell_space_segmentation' not found in zarr group",
    ):
        Labels.from_zarr(zarr_group)


def test_labels_invalid_dtype(store: Store) -> None:
    """
    Check that an invalid data type raises an error.
    """
    zarr_group = json_to_zarr_group(json_fname="labels_example.json", store=store)
    image_group = zarr_group.create_group("cell_space_segmentation")
    image_group.attrs.put(
        json_to_zarr_group(
            json_fname="labels_image_example.json", store=store
        ).attrs.asdict()
    )
    image_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype=np.float32,
        dimension_names=["t", "c", "z", "y", "x"],
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Data type of labels at path 'cell_space_segmentation/0' is not valid. "
            "Got float32, should be one of "
            "['uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32', 'uint64', 'int64']"
        ),
    ):
        Labels.from_zarr(zarr_group)
