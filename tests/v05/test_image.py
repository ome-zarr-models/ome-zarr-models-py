import re

import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

from ome_zarr_models.v05.axes import Axis
from ome_zarr_models.v05.coordinate_transformations import VectorScale
from ome_zarr_models.v05.image import Image, ImageAttrs
from ome_zarr_models.v05.multiscales import Dataset, Multiscale
from tests.v05.conftest import json_to_zarr_group


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

    assert ome_group.attributes.ome == ImageAttrs(
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


def test_image_no_dim_names(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="image_example.json", store=store)
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    arr1 = zarr_group.create_array("1", shape=(1, 1, 1, 1, 1), dtype="uint8")
    assert arr1.metadata.dimension_names is None  # type: ignore[union-attr]
    zarr_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    with pytest.raises(
        ValidationError,
        match="The array in this group at  '1' has no dimension_names metadata",
    ):
        Image.from_zarr(zarr_group)


def test_image_wrong_dim_names(store: Store) -> None:
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
        dimension_names=["t", "c", "z", "x", "y"],
    )
    zarr_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "The multiscale metadata has ('t', 'c', 'z', 'y', 'x') axes names "
            "which does not match the dimension names of the array "
            "found in this group at path '1' (('t', 'c', 'z', 'x', 'y'))"
        ),
    ):
        Image.from_zarr(zarr_group)
