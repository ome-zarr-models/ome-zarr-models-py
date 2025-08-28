import pytest
from zarr.abc.store import Store

from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.labels import LabelsAttrs
from tests.conftest import UnlistableStore
from tests.v04.conftest import json_to_zarr_group


def test_image_with_labels(store: Store) -> None:
    if isinstance(store, UnlistableStore):
        pytest.xfail("Labels do not work on unlistable stores")

    zarr_group = json_to_zarr_group(json_fname="multiscales_example.json", store=store)
    zarr_group.create_group("labels")
    zarr_group["labels"].create_array("labels0", shape=(1, 1), dtype="uint8")  # type: ignore[union-attr]
    zarr_group["labels"].attrs.put({"labels": ["labels0"]})

    zarr_group.create_array("0", shape=(1, 1, 1, 1), dtype="uint8")
    zarr_group.create_array("1", shape=(1, 1, 1, 1), dtype="uint8")

    ome_group = Image.from_zarr(zarr_group)
    labels_group = ome_group.labels
    assert labels_group is not None
    assert labels_group.attributes == LabelsAttrs(labels=["labels0"])
