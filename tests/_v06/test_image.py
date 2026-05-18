import pytest
from pydantic_zarr.v3 import AnyArraySpec, ArraySpec, NamedConfig
from zarr.abc.store import Store
from zarr.storage import MemoryStore

from ome_zarr_models._utils import TransformGraphNode
from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    CoordinateSystemIdentifier,
    Scale,
    Sequence,
    Translation,
)
from ome_zarr_models._v06.image import Image, ImageAttrs
from ome_zarr_models._v06.multiscales import Dataset, Multiscale

from .conftest import json_to_zarr_group


def test_image(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="image_example.json", store=store)
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "1",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    ome_group = Image.from_zarr(zarr_group)
    image_attrs = ImageAttrs(
        version="0.6",
        multiscales=[
            Multiscale(
                coordinateSystems=(
                    CoordinateSystem(
                        name="coord_sys0",
                        axes=(
                            Axis(
                                name="t",
                                type="time",
                                discrete=None,
                                unit="millisecond",
                                longName=None,
                            ),
                            Axis(
                                name="c",
                                type="channel",
                                discrete=None,
                                unit=None,
                                longName=None,
                            ),
                            Axis(
                                name="z",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                            Axis(
                                name="y",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                            Axis(
                                name="x",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                        ),
                    ),
                    CoordinateSystem(
                        name="coord_sys1",
                        axes=(
                            Axis(
                                name="t",
                                type="time",
                                discrete=None,
                                unit="millisecond",
                                longName=None,
                            ),
                            Axis(
                                name="c",
                                type="channel",
                                discrete=None,
                                unit=None,
                                longName=None,
                            ),
                            Axis(
                                name="z",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                            Axis(
                                name="y",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                            Axis(
                                name="x",
                                type="space",
                                discrete=None,
                                unit="micrometer",
                                longName=None,
                            ),
                        ),
                    ),
                ),
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            Scale(
                                type="scale",
                                input=CoordinateSystemIdentifier(path="0"),
                                output=CoordinateSystemIdentifier(name="coord_sys0"),
                                name=None,
                                scale=(1.0, 1.0, 0.5, 0.5, 0.5)
                            ),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            Scale(
                                type="scale",
                                input=CoordinateSystemIdentifier(path="1"),
                                output=CoordinateSystemIdentifier(name="coord_sys0"),
                                name=None,
                                scale=(1.0, 1.0, 1.0, 1.0, 1.0)
                            ),
                        ),
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=(
                            Scale(
                                type="scale",
                                input=CoordinateSystemIdentifier(path="2"),
                                output=CoordinateSystemIdentifier(name="coord_sys0"),
                                name=None,
                                scale=(1.0, 1.0, 2.0, 2.0, 2.0)
                            ),
                        ),
                    ),
                ),
                coordinateTransformations=(
                    Scale(
                        type="scale",
                        input=CoordinateSystemIdentifier(name="coord_sys0"),
                        output=CoordinateSystemIdentifier(name="coord_sys1"),
                        name=None,
                        scale=(0.1, 1.0, 1.0, 1.0, 1.0)
                    ),
                ),
                metadata={
                    "description": "the fields in metadata depend on the downscaling "
                    "implementation. Here, the parameters passed to the skimage "
                    "function are given",
                    "method": "skimage.transform.pyramid_gaussian",
                    "version": "0.16.1",
                    "args": "[true]",
                    "kwargs": {"multichannel": True},
                },
                name="example",
                type="gaussian",
            )
        ],
    )
    assert ome_group.attributes.ome == image_attrs


def test_image_new() -> None:
    # Spec for the full resolution data
    array_spec: AnyArraySpec = ArraySpec(
        shape=(100, 100),
        data_type="uint16",
        chunk_grid=NamedConfig(
            name="regular",
            configuration={"chunk_shape": [32, 32]},
        ),
        chunk_key_encoding=NamedConfig(
            name="default", configuration={"separator": "/"}
        ),
        fill_value=0,
        codecs=[NamedConfig(name="bytes")],
        dimension_names=["y", "x"],
        attributes={},
    )

    array_specs: list[AnyArraySpec] = [
        # Full res
        array_spec,
        # Half-res
        array_spec.model_copy(update={"shape": (50, 50)}),
    ]

    image = Image.new(
        array_specs=array_specs,
        paths=["0", "1"],
        scales=[[1, 1], [2, 2]],
        translations=[[0, 0], [1, 1]],
        name="my_image",
        physical_coord_system=CoordinateSystem(
            name="my_image_coords",
            axes=(
                Axis(name="y", type="space", unit="micrometer", discrete=False),
                Axis(name="x", type="space", unit="micrometer", discrete=False),
            ),
        ),
    )
    assert image.members == {
        "0": ArraySpec(
            zarr_format=3,
            node_type="array",
            attributes={},
            shape=(100, 100),
            data_type="uint16",
            chunk_grid={"name": "regular", "configuration": {"chunk_shape": (32, 32)}},
            chunk_key_encoding={"name": "default", "configuration": {"separator": "/"}},
            fill_value=0,
            codecs=({"name": "bytes"},),
            storage_transformers=(),
            dimension_names=("y", "x"),
        ),
        "1": ArraySpec(
            zarr_format=3,
            node_type="array",
            attributes={},
            shape=(50, 50),
            data_type="uint16",
            chunk_grid={"name": "regular", "configuration": {"chunk_shape": (32, 32)}},
            chunk_key_encoding={"name": "default", "configuration": {"separator": "/"}},
            fill_value=0,
            codecs=({"name": "bytes"},),
            storage_transformers=(),
            dimension_names=("y", "x"),
        ),
    }
    assert image.ome_attributes == ImageAttrs(
        version="0.6",
        multiscales=[
            Multiscale(
                coordinateSystems=(
                    CoordinateSystem(
                        name="my_image_coords",
                        axes=(
                            Axis(
                                name="y",
                                type="space",
                                discrete=False,
                                unit="micrometer",
                                longName=None,
                            ),
                            Axis(
                                name="x",
                                type="space",
                                discrete=False,
                                unit="micrometer",
                                longName=None,
                            ),
                        ),
                    ),
                ),
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            Sequence(
                                type="sequence",
                                input=CoordinateSystemIdentifier(path="0"),
                                output=CoordinateSystemIdentifier(
                                    name="my_image_coords"
                                ),
                                name=None,
                                transformations=(
                                    Scale(
                                        type="scale",
                                        input=None,
                                        output=None,
                                        name=None,
                                        scale=(1.0, 1.0),
                                    ),
                                    Translation(
                                        type="translation",
                                        input=None,
                                        output=None,
                                        name=None,
                                        translation=(0.0, 0.0),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            Sequence(
                                type="sequence",
                                input=CoordinateSystemIdentifier(path="1"),
                                output=CoordinateSystemIdentifier(
                                    name="my_image_coords"
                                ),
                                name=None,
                                transformations=(
                                    Scale(
                                        type="scale",
                                        input=None,
                                        output=None,
                                        name=None,
                                        scale=(2.0, 2.0),
                                    ),
                                    Translation(
                                        type="translation",
                                        input=None,
                                        output=None,
                                        name=None,
                                        translation=(1.0, 1.0),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                coordinateTransformations=(),
                metadata=None,
                name="my_image",
                type=None,
            )
        ],
    )


def test_transform_graph() -> None:
    zarr_group = json_to_zarr_group(
        json_fname="image_example.json", store=MemoryStore()
    )
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "1",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    image = Image.from_zarr(zarr_group)

    graph = image.transform_graph()
    assert graph._graph == {
        TransformGraphNode(name="coord_sys0", path=None): {
            TransformGraphNode(name="coord_sys1", path=None): Scale(
                type="scale",
                input=CoordinateSystemIdentifier(name="coord_sys0"),
                output=CoordinateSystemIdentifier(name="coord_sys1"),
                name=None,
                scale=(0.1, 1.0, 1.0, 1.0, 1.0),
            )
        },
        TransformGraphNode(name=None, path="0"): {
            TransformGraphNode(name="coord_sys0", path=None): Scale(
                type="scale",
                input=CoordinateSystemIdentifier(path="0"),
                output=CoordinateSystemIdentifier(name="coord_sys0"),
                name=None,
                scale=(1.0, 1.0, 0.5, 0.5, 0.5),
            )
        },
        TransformGraphNode(name=None, path="1"): {
            TransformGraphNode(name="coord_sys0", path=None): Scale(
                type="scale",
                input=CoordinateSystemIdentifier(path="1"),
                output=CoordinateSystemIdentifier(name="coord_sys0"),
                name=None,
                scale=(1.0, 1.0, 1.0, 1.0, 1.0),
            )
        },
        TransformGraphNode(name=None, path="2"): {
            TransformGraphNode(name="coord_sys0", path=None): Scale(
                type="scale",
                input=CoordinateSystemIdentifier(path="2"),
                output=CoordinateSystemIdentifier(name="coord_sys0"),
                name=None,
                scale=(1.0, 1.0, 2.0, 2.0, 2.0),
            )
        },
    }


def test_transform_graph_to_graphviz() -> None:
    graphviz = pytest.importorskip("graphviz")
    # Test rendering a transform graph to a graphviz graph
    # NOTE: currently just a smoke test, does not check that the output is correct
    zarr_group = json_to_zarr_group(
        json_fname="image_example.json", store=MemoryStore()
    )
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "1",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    zarr_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    image = Image.from_zarr(zarr_group)

    graph = image.transform_graph()
    graphviz_graph = graph.to_graphviz()
    assert isinstance(graphviz_graph, graphviz.Digraph)
