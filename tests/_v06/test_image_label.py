from zarr.abc.store import Store

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import VectorScale
from ome_zarr_models._v06.image_label import ImageLabel, ImageLabelAttrs
from ome_zarr_models._v06.image_label_types import Color, Label, Source
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from tests._v06.conftest import json_to_zarr_group


def test_image_label(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="image_label_example.json", store=store)
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
    ome_group = ImageLabel.from_zarr(zarr_group)
    assert ome_group.attributes.ome == ImageLabelAttrs(
        image_label=Label(
            colors=(
                Color(label_value=0, rgba=(0, 0, 128, 128)),
                Color(label_value=1, rgba=(0, 128, 0, 128)),
            ),
            properties=[
                {
                    "label_value": 0,
                    "area (pixels)": 1200,
                    "class": "intercellular space",
                },
                {
                    "label_value": 1,
                    "area (pixels)": 1650,
                    "class": "cell",
                    "cell type": "neuron",
                },
            ],
            source=Source(image="../../"),
            version=None,
        ),
        multiscales=[
            Multiscale(
                axes=[
                    Axis(name="t", type="time", unit="millisecond"),
                    Axis(name="c", type="channel", unit=None),
                    Axis(name="z", type="space", unit="micrometer"),
                    Axis(name="y", type="space", unit="micrometer"),
                    Axis(name="x", type="space", unit="micrometer"),
                ],
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 0.5, 0.5, 0.5]),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 1.0, 1.0, 1.0]),
                        ),
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 2.0, 2.0, 2.0]),
                        ),
                    ),
                ),
                coordinateTransformations=(
                    VectorScale(type="scale", scale=[0.1, 1.0, 1.0, 1.0, 1.0]),
                ),
                metadata={
                    "description": (
                        "the fields in metadata depend on the downscaling "
                        "implementation. Here, the parameters passed to the skimage "
                        "function are given"
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
        version="0.6",
    )
