from zarr.abc.store import Store

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    VectorScale,
)
from ome_zarr_models._v06.image import Image, ImageAttrs
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from tests._v06.conftest import json_to_zarr_group


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
                            VectorScale(
                                scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                                input="/0",
                                output="example",
                            )
                        ],
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=[
                            VectorScale(
                                scale=[1.0, 1.0, 1.0, 1.0, 1.0],
                                input="/1",
                                output="example",
                            )
                        ],
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=[
                            VectorScale(
                                scale=[1.0, 1.0, 2.0, 2.0, 2.0],
                                input="/2",
                                output="example",
                            )
                        ],
                    ),
                ),
                coordinateTransformations=(
                    VectorScale(
                        scale=[0.1, 1.0, 1.0, 1.0, 1.0],
                        input="example",
                        output="example2",
                    ),
                ),
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
        version="0.6",
    )
    print(image_attrs.model_dump_json(indent=4))
    assert ome_group.attributes.ome == image_attrs


# TODO: copy over and adapt additional tests from v05
