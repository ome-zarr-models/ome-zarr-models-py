from ome_zarr_models._v05.image_label import ImageLabel
from tests.v05.conftest import json_to_zarr_group


def test_image_label() -> None:
    zarr_group = json_to_zarr_group(json_fname="image_label_example.json")
    ome_group = ImageLabel.from_zarr(zarr_group)
    assert ome_group.ome_attributes == None
