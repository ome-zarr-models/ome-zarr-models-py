from ome_zarr_models._v05.labels import Labels, LabelsAttrs
from tests.v05.conftest import json_to_zarr_group


def test_labels() -> None:
    zarr_group = json_to_zarr_group(json_fname="labels_example.json")
    ome_group = Labels.from_zarr(zarr_group)
    assert ome_group.attributes.ome == LabelsAttrs(
        labels=["cell_space_segmentation"], version="0.5"
    )
