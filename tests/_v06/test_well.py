import pytest
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


def test_well_image_constraint() -> None:
    well = WellMeta(
        images=[
            WellImage(path="0_1", acquisition=1),
            WellImage(path="1_1", acquisition=1),
            WellImage(path="2-1", acquisition=2),
            WellImage(path="3-1", acquisition=2),
        ],
        version="0.6",
    )

    assert well.get_acquisition_paths() == {1: ["0_1", "1_1"], 2: ["2-1", "3-1"]}


def test_well_image_constraint_fails_period() -> None:
    with pytest.raises(ValueError, match="Invalid node name"):
        WellMeta(
            images=[
                WellImage(path=".", acquisition=1),
            ],
            version="0.6",
        )


def test_well_image_constraint_fails_double_underscore() -> None:
    with pytest.raises(ValueError, match="Invalid node name"):
        WellMeta(
            images=[
                WellImage(path="__image", acquisition=1),
            ],
            version="0.6",
        )
