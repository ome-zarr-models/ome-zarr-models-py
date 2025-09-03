import re

import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    VectorScale,
)
from ome_zarr_models._v06.image import Image, ImageAttrs
from ome_zarr_models._v06.labels import LabelsAttrs
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from tests._v06.conftest import json_to_zarr_group, json_to_dict


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


# TODO: this test was copy-pasted from v05 and needs to be adjusted
# def test_image_no_dim_names(store: Store) -> None:
#     zarr_group = json_to_zarr_group(json_fname="image_example.json", store=store)
#     zarr_group.create_array(
#         "0",
#         shape=(1, 1, 1, 1, 1),
#         dtype="uint8",
#         dimension_names=["t", "c", "z", "y", "x"],
#     )
#     arr1 = zarr_group.create_array("1", shape=(1, 1, 1, 1, 1), dtype="uint8")
#     assert arr1.metadata.dimension_names is None  # type: ignore[union-attr]
#     zarr_group.create_array(
#         "2",
#         shape=(1, 1, 1, 1, 1),
#         dtype="uint8",
#         dimension_names=["t", "c", "z", "y", "x"],
#     )
#     with pytest.raises(
#         ValidationError,
#         match="The array in this group at  '1' has no dimension_names metadata",
#     ):
#         Image.from_zarr(zarr_group)


# TODO: this test was copy-pasted from v05 and needs to be adjusted
# def test_image_wrong_dim_names(store: Store) -> None:
#     zarr_group = json_to_zarr_group(json_fname="image_example.json", store=store)
#     zarr_group.create_array(
#         "0",
#         shape=(1, 1, 1, 1, 1),
#         dtype="uint8",
#         dimension_names=["t", "c", "z", "y", "x"],
#     )
#     zarr_group.create_array(
#         "1",
#         shape=(1, 1, 1, 1, 1),
#         dtype="uint8",
#         dimension_names=["t", "c", "z", "x", "y"],
#     )
#     zarr_group.create_array(
#         "2",
#         shape=(1, 1, 1, 1, 1),
#         dtype="uint8",
#         dimension_names=["t", "c", "z", "y", "x"],
#     )
#     with pytest.raises(
#         ValidationError,
#         match=re.escape(
#             "The multiscale metadata has ('t', 'c', 'z', 'y', 'x') axes names "
#             "which does not match the dimension names of the array "
#             "found in this group at path '1' (('t', 'c', 'z', 'x', 'y'))"
#         ),
#     ):
#         Image.from_zarr(zarr_group)


def test_image_with_labels(store: Store) -> None:
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
    # Add labels group
    labels_group = zarr_group.create_group(
        "labels",
        attributes=json_to_dict(json_fname="labels_example.json"),
    )

    with pytest.raises(
        ValueError, match="Label path 'cell_space_segmentation' not found in zarr group"
    ):
        Image.from_zarr(zarr_group)

    # Add image labels group
    image_label_group = labels_group.create_group(
        "cell_space_segmentation",
        attributes=json_to_dict(json_fname="image_label_example.json"),
    )
    image_label_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    image_label_group.create_array(
        "1",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    image_label_group.create_array(
        "2",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    image = Image.from_zarr(zarr_group)
    assert image.labels is not None
    assert image.labels.attributes.ome == LabelsAttrs(
        version="0.6", labels=["cell_space_segmentation"]
    )


def test_image_with_labels_mismatch_multiscales(store: Store) -> None:
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
    # Add labels group
    labels_group = zarr_group.create_group(
        "labels",
        attributes=json_to_dict(json_fname="labels_example.json"),
    )
    # Add image labels group
    image_label_group = labels_group.create_group(
        "cell_space_segmentation",
        attributes=json_to_dict(json_fname="labels_image_example.json"),
    )
    image_label_group.create_array(
        "0",
        shape=(1, 1, 1, 1, 1),
        dtype="uint8",
        dimension_names=["t", "c", "z", "y", "x"],
    )
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Number of image label multiscale levels (1) doesn't match "
            "number of image multiscale levels (3)."
        ),
    ):
        Image.from_zarr(zarr_group)