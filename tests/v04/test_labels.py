from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.labels import LabelsAttrs
from tests.v04.conftest import json_to_zarr_group


def test_image_with_labels() -> None:
    zarr_group = json_to_zarr_group(json_fname="multiscales_example.json")
    zarr_group.create_group("labels")
    zarr_group["labels"].create_dataset("labels0", shape=(1, 1))
    zarr_group["labels"].attrs.put({"labels": ["labels0"]})

    zarr_group.create_dataset("0", shape=(1, 1, 1, 1))
    zarr_group.create_dataset("1", shape=(1, 1, 1, 1))

    ome_group = Image.from_zarr(zarr_group)
    labels_group = ome_group.labels
    assert labels_group is not None
    assert labels_group.attributes == LabelsAttrs(labels=["labels0"])
