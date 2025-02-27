from ome_zarr_models._v05.well import Well, WellAttrs
from ome_zarr_models._v05.well_types import WellImage, WellMeta
from tests.v05.conftest import json_to_zarr_group


def test_well() -> None:
    zarr_group = json_to_zarr_group(json_fname="well_example.json")
    ome_group = Well.from_zarr(zarr_group)
    assert ome_group.attributes.ome == WellAttrs(
        version="0.5",
        well=WellMeta(
            images=[
                WellImage(path="0", acquisition=1),
                WellImage(path="1", acquisition=1),
                WellImage(path="2", acquisition=2),
                WellImage(path="3", acquisition=2),
            ],
            version="0.5",
        ),
    )
