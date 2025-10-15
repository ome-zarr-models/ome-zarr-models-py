from pydantic_zarr.v3 import AnyArraySpec, ArraySpec, NamedConfig
from zarr.abc.store import Store

from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
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
                        axes=[
                            Axis(name="t", type="time", unit="millisecond"),
                            Axis(name="c", type="channel", unit=None),
                            Axis(name="z", type="space", unit="micrometer"),
                            Axis(name="y", type="space", unit="micrometer"),
                            Axis(name="x", type="space", unit="micrometer"),
                        ],
                    ),
                    CoordinateSystem(
                        name="coord_sys1",
                        axes=[
                            Axis(name="t", type="time", unit="millisecond"),
                            Axis(name="c", type="channel", unit=None),
                            Axis(name="z", type="space", unit="micrometer"),
                            Axis(name="y", type="space", unit="micrometer"),
                            Axis(name="x", type="space", unit="micrometer"),
                        ],
                    ),
                ),
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=[
                            Scale(
                                type="scale",
                                input="/0",
                                output="coord_sys0",
                                name=None,
                                scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                            )
                        ],
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=[
                            Scale(
                                type="scale",
                                input="/1",
                                output="coord_sys0",
                                name=None,
                                scale=[1.0, 1.0, 1.0, 1.0, 1.0],
                            )
                        ],
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=[
                            Scale(
                                type="scale",
                                input="/2",
                                output="coord_sys0",
                                name=None,
                                scale=[1.0, 1.0, 2.0, 2.0, 2.0],
                            )
                        ],
                    ),
                ),
                coordinateTransformations=(
                    Scale(
                        type="scale",
                        input="coord_sys0",
                        output="coord_sys1",
                        name=None,
                        scale=[0.1, 1.0, 1.0, 1.0, 1.0],
                    ),
                ),
                metadata={
                    "description": (
                        "the fields in metadata depend on "
                        "the downscaling implementation. Here, the "
                        "parameters passed to the skimage function are given"
                    ),
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
    print(image_attrs.model_dump_json(indent=4))
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
        output_coord_transform=Scale(
            scale=(
                0.5,
                0.2,
            )
        ),
        output_coord_system=CoordinateSystem(
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
                        name="my_image_array_coords",
                        axes=(
                            Axis(
                                name="y",
                                type="array",
                                discrete=True,
                                unit=None,
                                longName=None,
                            ),
                            Axis(
                                name="x",
                                type="array",
                                discrete=True,
                                unit=None,
                                longName=None,
                            ),
                        ),
                    ),
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
                                input="0",
                                output="my_image_array_coords",
                                name=None,
                                transformations=(
                                    Scale(
                                        type="scale",
                                        input=None,
                                        output=None,
                                        name=None,
                                        scale=(1.0, 1.0),
                                        path=None,
                                    ),
                                    Translation(
                                        type="translation",
                                        input=None,
                                        output=None,
                                        name=None,
                                        translation=(0.0, 0.0),
                                        path=None,
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
                                input="1",
                                output="my_image_array_coords",
                                name=None,
                                transformations=(
                                    Scale(
                                        type="scale",
                                        input=None,
                                        output=None,
                                        name=None,
                                        scale=(2.0, 2.0),
                                        path=None,
                                    ),
                                    Translation(
                                        type="translation",
                                        input=None,
                                        output=None,
                                        name=None,
                                        translation=(1.0, 1.0),
                                        path=None,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                coordinateTransformations=(
                    Scale(
                        type="scale",
                        input="my_image_array_coords",
                        output="my_image_coords",
                        name=None,
                        scale=(0.5, 0.2),
                        path=None,
                    ),
                ),
                metadata=None,
                name="my_image",
                type=None,
            )
        ],
    )
