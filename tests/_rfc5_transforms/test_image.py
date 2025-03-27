from ome_zarr_models._rfc5_transforms.axes import Axis
from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
)
from ome_zarr_models._rfc5_transforms.image import Image, ImageAttrs
from ome_zarr_models._rfc5_transforms.multiscales import Dataset, Multiscale
from tests._rfc5_transforms.conftest import json_to_zarr_group


def test_image() -> None:
    zarr_group = json_to_zarr_group(json_fname="image_example.json")
    ome_group = Image.from_zarr(zarr_group)
    image_attrs = ImageAttrs(
        multiscales=[
            Multiscale(
                coordinateSystems=(
                    CoordinateSystem(
                        name="example",
                        axes=[
                            Axis(name="t", type="time", unit="millisecond"),
                            Axis(name="c", type="channel", unit=None),
                            Axis(name="z", type="space", unit="micrometer"),
                            Axis(name="y", type="space", unit="micrometer"),
                            Axis(name="x", type="space", unit="micrometer"),
                        ],
                    ),
                    CoordinateSystem(
                        name="example2",
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
                            CoordinateTransformation(
                                type="scale",
                                scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                                input="/0",
                                output="example",
                            )
                        ],
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=[
                            CoordinateTransformation(
                                type="scale",
                                scale=[1.0, 1.0, 1.0, 1.0, 1.0],
                                input="/1",
                                output="example",
                            )
                        ],
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=[
                            CoordinateTransformation(
                                type="scale",
                                scale=[1.0, 1.0, 2.0, 2.0, 2.0],
                                input="/2",
                                output="example",
                            )
                        ],
                    ),
                ),
                coordinateTransformations=[
                    CoordinateTransformation(
                        type="scale",
                        scale=[0.1, 1.0, 1.0, 1.0, 1.0],
                        input="example",
                        output="example2",
                    )
                ],
                metadata={
                    "description": "the fields in metadata depend on the downscaling "
                    "implementation. Here, the parameters passed to the "
                    "skimage function are given",
                    "method": "skimage.transform.pyramid_gaussian",
                    "version": "0.16.1",
                    "args": "[true]",
                    "kwargs": {"multichannel": True},
                },
                name="example",
                type="gaussian",
            )
        ],
        version="0.5",
    )
    print(image_attrs.model_dump_json(indent=4))
    assert ome_group.attributes.ome == image_attrs
