from pathlib import Path

import zarr
from pydantic_zarr.v3 import AnyArraySpec, ArraySpec, GroupSpec, NamedConfig

from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    CoordinateSystemIdentifier,
    Translation,
)
from ome_zarr_models._v06.image import Image
from ome_zarr_models._v06.scene import BaseSceneAttrs, Scene, SceneAttrs


def test_load_container() -> None:
    group = zarr.open_group(
        Path(__file__).parent.parent
        / "data"
        / "examples"
        / "v06"
        / "stitched_tiles_2d.zarr"
    )
    container = Scene.from_zarr(group)
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
    assert container.ome_attributes == BaseSceneAttrs(
        version="0.6",
        scene=SceneAttrs(
            coordinateTransformations=(
                Translation(
                    type="translation",
                    input=CoordinateSystemIdentifier(name="physical", path="tile_0"),
                    output="world",
                    name="tile_0_mm to world",
                    translation=(0.0, 0.0),
                    path=None,
                ),
                Translation(
                    type="translation",
                    input=CoordinateSystemIdentifier(name="physical", path="tile_1"),
                    output="world",
                    name="tile_1_mm to world",
                    translation=(0.0, 348.0),
                    path=None,
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
        ),
    )


def test_scene_new() -> None:
    # Create array spec
    array_spec: AnyArraySpec = ArraySpec(
        zarr_format=3,
        node_type="array",
        attributes={},
        shape=(256, 256),
        data_type="uint8",
        chunk_grid=NamedConfig(
            name="regular",
            configuration={"chunk_shape": [256, 256]},
        ),
        chunk_key_encoding=NamedConfig(
            name="default", configuration={"separator": "/"}
        ),
        fill_value=0,
        codecs=[NamedConfig(name="bytes")],
        dimension_names=["y", "x"],
    )

    # Create coordinate system
    physical_coord_system = CoordinateSystem(
        name="physical_coord_system",
        axes=(
            Axis(name="y", type="space", unit="um"),
            Axis(name="x", type="space", unit="um"),
        ),
    )

    world_coord_system = CoordinateSystem(
        name="world",
        axes=(
            Axis(name="y", type="space", unit="um"),
            Axis(name="x", type="space", unit="um"),
        ),
    )

    # Create images
    image_a = Image.new(
        array_specs=[array_spec],
        paths=["0"],
        scales=[[1, 1]],
        translations=[[0, 0]],
        physical_coord_system=physical_coord_system,
        name="image_a",
    )

    image_b = Image.new(
        array_specs=[array_spec],
        paths=["0"],
        scales=[[1, 1]],
        translations=[[0, 0]],
        physical_coord_system=physical_coord_system,
        name="image_b",
    )

    # Create scene with coordinate transformations
    transform_a_world = Translation(
        translation=(0, 0),
        input="image_a",
        output="world",
    )
    transform_b_world = Translation(
        translation=(0, 256),
        input="image_b",
        output="world",
    )

    scene = Scene.new(
        images={"image_a": image_a, "image_b": image_b},
        coord_transforms=[transform_a_world, transform_b_world],
        coord_systems=[world_coord_system],
    )

    # Verify scene structure
    assert scene.members is not None
    assert "image_a" in scene.members
    assert "image_b" in scene.members

    # Verify that members are GroupSpecs with nested ArraySpecs
    image_a_member = scene.members["image_a"]
    assert isinstance(image_a_member, GroupSpec)
    assert image_a_member.members is not None
    assert "0" in image_a_member.members
    assert isinstance(image_a_member.members["0"], ArraySpec)

    image_b_member = scene.members["image_b"]
    assert isinstance(image_b_member, GroupSpec)
    assert image_b_member.members is not None
    assert "0" in image_b_member.members
    assert isinstance(image_b_member.members["0"], ArraySpec)

    # Verify array specs have correct shapes
    assert isinstance(scene.members["image_a"], GroupSpec)
    assert scene.members["image_a"].members is not None
    assert scene.members["image_a"].members["0"].shape == (256, 256)
    assert isinstance(scene.members["image_b"], GroupSpec)
    assert scene.members["image_b"].members is not None
    assert scene.members["image_b"].members["0"].shape == (256, 256)

    # Verify coordinate transformations
    assert len(scene.ome_attributes.scene.coordinateTransformations) == 2
    coord_transform_0 = scene.ome_attributes.scene.coordinateTransformations[0]
    assert isinstance(coord_transform_0, Translation)
    assert coord_transform_0.input == "image_a"
    assert coord_transform_0.output == "world"
    assert coord_transform_0.translation == (0, 0)
    coord_transform_1 = scene.ome_attributes.scene.coordinateTransformations[1]
    assert isinstance(coord_transform_1, Translation)
    assert coord_transform_1.input == "image_b"
    assert coord_transform_1.output == "world"
    assert coord_transform_1.translation == (0, 256)

    # Verify coordinate systems
    assert len(scene.ome_attributes.scene.coordinateSystems) == 1
    assert scene.ome_attributes.scene.coordinateSystems[0].name == "world"

    # Verify version
    assert scene.ome_attributes.version == "0.6"
