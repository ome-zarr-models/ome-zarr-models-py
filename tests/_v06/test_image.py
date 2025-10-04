from zarr.abc.store import Store

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transforms import (
    CoordinateSystem,
    Scale,
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
