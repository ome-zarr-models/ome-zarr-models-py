from zarr.abc.store import Store

from ome_zarr_models._v06.well import Well, WellAttrs
from ome_zarr_models._v06.well_types import WellImage, WellMeta
from tests._v06.conftest import json_to_zarr_group


def test_well(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="well_example.json", store=store)
    ome_group = Well.from_zarr(zarr_group)
    assert ome_group.attributes.ome == WellAttrs(
        version="0.6",
        well=WellMeta(
            images=[
                WellImage(path="0", acquisition=1),
                WellImage(path="1", acquisition=1),
                WellImage(path="2", acquisition=2),
                WellImage(path="3", acquisition=2),
            ],
            version="0.6",
        ),
    )


def test_get_paths() -> None:
    well = WellMeta(
        images=[
            WellImage(path="0", acquisition=1),
            WellImage(path="1", acquisition=1),
            WellImage(path="2", acquisition=2),
            WellImage(path="3", acquisition=2),
        ],
        version="0.6",
    )

    assert well.get_acquisition_paths() == {1: ["0", "1"], 2: ["2", "3"]}
