from pathlib import Path

import zarr

from ome_zarr_models._v06.container import Container, ContainerAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    Transform,
    Translation,
)


def test_load_container() -> None:
    group = zarr.open_group(
        Path(__file__).parent.parent
        / "data"
        / "examples"
        / "v06"
        / "stitched_tiles_2d.zarr"
    )
    container = Container.from_zarr(group)
    assert container.members == {}
    assert container.ome_attributes == ContainerAttrs(
        version="0.6",
        coordinateTransformations=(
            Translation(
                type="translation",
                input="/tile_0",
                output="world",
                name="tile_0_mm to world",
                translation=[0, 0],
            ),
            Translation(
                type="translation",
                input="/tile_1",
                output="world",
                name="tile_1_mm to world",
                translation=[0, 348],
            ),
        ),
        coordinateSystems=(
            CoordinateSystem(
                name="world",
                axes=(
                    Axis(
                        name="x",
                        type="space",
                        discrete=False,
                        unit="micrometer",
                        longName=None,
                    ),
                    Axis(
                        name="y",
                        type="space",
                        discrete=False,
                        unit="micrometer",
                        longName=None,
                    ),
                ),
            ),
        ),
    )
