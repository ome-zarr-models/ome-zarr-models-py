from pathlib import Path

import zarr
from pydantic_zarr.v3 import ArraySpec, GroupSpec

from ome_zarr_models._v06.container import Container, ContainerAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
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
    assert container.members == {
        "tile_0": GroupSpec(
            zarr_format=3,
            node_type="group",
            attributes={
                "ome": {
                    "version": "0.6.dev1",
                    "multiscales": [
                        {
                            "coordinateSystems": (
                                {
                                    "name": "physical",
                                    "axes": (
                                        {
                                            "name": "y",
                                            "type": "space",
                                            "discrete": False,
                                            "unit": "micrometer",
                                            "longName": None,
                                        },
                                        {
                                            "name": "x",
                                            "type": "space",
                                            "discrete": False,
                                            "unit": "micrometer",
                                            "longName": None,
                                        },
                                    ),
                                },
                            ),
                            "datasets": (
                                {
                                    "path": "0",
                                    "coordinateTransformations": (
                                        {
                                            "type": "scale",
                                            "input": "0",
                                            "output": "physical",
                                            "name": "tile_0 to physical",
                                            "scale": (1.0, 1.0),
                                            "path": None,
                                        },
                                    ),
                                },
                            ),
                            "coordinateTransformations": None,
                            "metadata": None,
                            "name": "multiscales",
                            "type": None,
                        }
                    ],
                }
            },
            members={
                "0": ArraySpec(
                    zarr_format=3,
                    node_type="array",
                    attributes={},
                    shape=(300, 372),
                    data_type="uint8",
                    chunk_grid={
                        "name": "regular",
                        "configuration": {"chunk_shape": (300, 372)},
                    },
                    chunk_key_encoding={
                        "name": "default",
                        "configuration": {"separator": "/"},
                    },
                    fill_value=0,
                    codecs=(
                        {"name": "bytes"},
                        {
                            "name": "zstd",
                            "configuration": {"level": 3, "checksum": False},
                        },
                    ),
                    storage_transformers=(),
                    dimension_names=None,
                )
            },
        ),
        "tile_1": GroupSpec(
            zarr_format=3,
            node_type="group",
            attributes={
                "ome": {
                    "version": "0.6.dev1",
                    "multiscales": [
                        {
                            "coordinateSystems": (
                                {
                                    "name": "physical",
                                    "axes": (
                                        {
                                            "name": "y",
                                            "type": "space",
                                            "discrete": False,
                                            "unit": "micrometer",
                                            "longName": None,
                                        },
                                        {
                                            "name": "x",
                                            "type": "space",
                                            "discrete": False,
                                            "unit": "micrometer",
                                            "longName": None,
                                        },
                                    ),
                                },
                            ),
                            "datasets": (
                                {
                                    "path": "0",
                                    "coordinateTransformations": (
                                        {
                                            "type": "scale",
                                            "input": "0",
                                            "output": "physical",
                                            "name": "tile_1 to physical",
                                            "scale": (1.0, 1.0),
                                            "path": None,
                                        },
                                    ),
                                },
                            ),
                            "coordinateTransformations": None,
                            "metadata": None,
                            "name": "multiscales",
                            "type": None,
                        }
                    ],
                }
            },
            members={
                "0": ArraySpec(
                    zarr_format=3,
                    node_type="array",
                    attributes={},
                    shape=(300, 372),
                    data_type="uint8",
                    chunk_grid={
                        "name": "regular",
                        "configuration": {"chunk_shape": (300, 372)},
                    },
                    chunk_key_encoding={
                        "name": "default",
                        "configuration": {"separator": "/"},
                    },
                    fill_value=0,
                    codecs=(
                        {"name": "bytes"},
                        {
                            "name": "zstd",
                            "configuration": {"level": 3, "checksum": False},
                        },
                    ),
                    storage_transformers=(),
                    dimension_names=None,
                )
            },
        ),
    }
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

    assert container.coordinate_systems == (
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
    )

    assert container.coordinate_transforms == (
        Translation(
            type="translation",
            input="/tile_0",
            output="world",
            name="tile_0_mm to world",
            translation=(0.0, 0.0),
            path=None,
        ),
        Translation(
            type="translation",
            input="/tile_1",
            output="world",
            name="tile_1_mm to world",
            translation=(0.0, 348.0),
            path=None,
        ),
    )
