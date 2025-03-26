import re

import pytest
from pydantic import ValidationError

from ome_zarr_models._v05.axes import Axis
from ome_zarr_models._v05.coordinate_transformations import VectorScale
from ome_zarr_models._v05.image import Image, ImageAttrs
from ome_zarr_models._v05.multiscales import Dataset, Multiscale
from tests.v05.conftest import json_to_zarr_group


def test_image() -> None:
    zarr_group = json_to_zarr_group(json_fname="image_example.json")
    ome_group = Image.from_zarr(zarr_group)
    assert ome_group.attributes.ome == ImageAttrs(
        version="0.5",
        multiscales=[
            Multiscale(
                axes=[
                    Axis(
                        name="t",
                        type="time",
                        unit="millisecond",
                        anatomicalOrientation="left-to-right",
                    ),
                    Axis(
                        name="c", type="channel", unit=None, anatomicalOrientation=None
                    ),
                    Axis(
                        name="z",
                        type="space",
                        unit="micrometer",
                        anatomicalOrientation=None,
                    ),
                    Axis(
                        name="y",
                        type="space",
                        unit="micrometer",
                        anatomicalOrientation=None,
                    ),
                    Axis(
                        name="x",
                        type="space",
                        unit="micrometer",
                        anatomicalOrientation=None,
                    ),
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


def test_invalid_orientations() -> None:
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Only one of ['right-to-left', 'left-to-right'] allowed in a set of axes."
        ),
    ):
        Multiscale(
            axes=[
                Axis(
                    name="z",
                    type="space",
                    unit="micrometer",
                    anatomicalOrientation="left-to-right",
                ),
                Axis(
                    name="y",
                    type="space",
                    unit="micrometer",
                    anatomicalOrientation="right-to-left",
                ),
            ],
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=(
                        VectorScale(type="scale", scale=[1.0, 1.0]),
                    ),
                ),
            ),
        )
