from zarr.abc.store import Store

from ome_zarr_models.v04.well import Well, WellAttrs
from ome_zarr_models.v04.well_types import WellImage, WellMeta
from tests.v04.conftest import json_to_zarr_group


def test_well(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="well_example_1.json", store=store)
    ome_group = Well.from_zarr(zarr_group)
    assert ome_group.attributes == WellAttrs(
        well=WellMeta(
            images=[
                WellImage(path="0", acquisition=1),
                WellImage(path="1", acquisition=1),
                WellImage(path="2", acquisition=2),
                WellImage(path="3", acquisition=2),
            ],
            version="0.4",
        )
    )

    zarr_group = json_to_zarr_group(json_fname="well_example_2.json", store=store)
    ome_group = Well.from_zarr(zarr_group)
    assert ome_group.attributes == WellAttrs(
        well=WellMeta(
            images=[
                WellImage(path="0", acquisition=0),
                WellImage(path="1", acquisition=3),
            ],
            version="0.4",
        )
    )


def test_get_paths() -> None:
    well = WellMeta(
        images=[
            WellImage(path="0", acquisition=1),
            WellImage(path="1", acquisition=1),
            WellImage(path="2", acquisition=2),
            WellImage(path="3", acquisition=2),
        ],
        version="0.4",
    )

    assert well.get_acquisition_paths() == {1: ["0", "1"], 2: ["2", "3"]}
