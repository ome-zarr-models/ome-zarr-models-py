import re

import numpy as np
import pytest
from pydantic_zarr.v2 import ArraySpec
from zarr.abc.store import Store

from ome_zarr_models.common.coordinate_transformations import VectorTranslation
from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.coordinate_transformations import VectorScale
from ome_zarr_models.v04.image import Image, ImageAttrs
from ome_zarr_models.v04.multiscales import Dataset, Multiscale
from tests.v04.conftest import json_to_zarr_group


def test_image(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="multiscales_example.json", store=store)
    zarr_group.create_array(
        "0",
        shape=(1, 1, 1, 1),
        dtype="uint8",
    )
    zarr_group.create_array("1", shape=(1, 1, 1, 1), dtype="uint8")

    ome_group = Image.from_zarr(zarr_group)
    assert ome_group.attributes == ImageAttrs(
        multiscales=[
            Multiscale(
                axes=[
                    Axis(name="c", type="channel", unit=None),
                    Axis(name="z", type="space", unit="micrometer"),
                    Axis(name="y", type="space", unit="micrometer"),
                    Axis(name="x", type="space", unit="micrometer"),
                ],
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            VectorScale(
                                type="scale",
                                scale=[
                                    1.0,
                                    0.5002025531914894,
                                    0.3603981534640209,
                                    0.3603981534640209,
                                ],
                            ),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            VectorScale(
                                type="scale",
                                scale=[
                                    1.0,
                                    0.5002025531914894,
                                    0.7207963069280418,
                                    0.7207963069280418,
                                ],
                            ),
                        ),
                    ),
                ),
                version="0.4",
                coordinateTransformations=None,
                metadata=None,
                name=None,
                type=None,
            )
        ],
        omero=None,
        _creator={"name": "omero-zarr", "version": "0.4.0"},
    )


def test_new_image() -> None:
    new_image = Image.new(
        array_specs=[
            ArraySpec(shape=(5, 5), chunks=(2, 2), dtype=np.uint8),
            ArraySpec(shape=(3, 3), chunks=(2, 2), dtype=np.uint8),
        ],
        paths=["scale0", "scale1"],
        axes=[
            Axis(name="x", type="space", unit="km"),
            Axis(name="y", type="space", unit="km"),
        ],
        scales=[(4, 4), (8, 8)],
        translations=[(2, 2), (4, 4)],
        name="new_image_test",
        multiscale_type="local mean",
        metadata={"key": "val"},
        global_scale=(-1, 1),
        global_translation=(10, 10),
    )
    assert new_image == Image(
        attributes=ImageAttrs(
            multiscales=[
                Multiscale(
                    axes=(
                        Axis(name="x", type="space", unit="km"),
                        Axis(name="y", type="space", unit="km"),
                    ),
                    datasets=(
                        Dataset(
                            path="scale0",
                            coordinateTransformations=(
                                VectorScale(type="scale", scale=[4.0, 4.0]),
                                VectorTranslation(
                                    type="translation", translation=[2.0, 2.0]
                                ),
                            ),
                        ),
                        Dataset(
                            path="scale1",
                            coordinateTransformations=(
                                VectorScale(type="scale", scale=[8.0, 8.0]),
                                VectorTranslation(
                                    type="translation", translation=[4.0, 4.0]
                                ),
                            ),
                        ),
                    ),
                    coordinateTransformations=(
                        VectorScale(type="scale", scale=[-1.0, 1.0]),
                        VectorTranslation(type="translation", translation=[10.0, 10.0]),
                    ),
                    metadata={"key": "val"},
                    name="new_image_test",
                    type="local mean",
                    version="0.4",
                )
            ],
            omero=None,
        ),
        members={
            "scale0": ArraySpec(
                attributes={},
                shape=(5, 5),
                chunks=(2, 2),
                dtype="|u1",
                fill_value=0,
                order="C",
                filters=None,
                dimension_separator="/",
                compressor=None,
            ),
            "scale1": ArraySpec(
                attributes={},
                shape=(3, 3),
                chunks=(2, 2),
                dtype="|u1",
                fill_value=0,
                order="C",
                filters=None,
                dimension_separator="/",
                compressor=None,
            ),
        },
    )


@pytest.fixture
def example_image() -> Image:
    return Image.new(
        array_specs=[
            ArraySpec(shape=(5, 5), chunks=(2, 2), dtype=np.uint8),
            ArraySpec(shape=(3, 3), chunks=(2, 2), dtype=np.uint8),
        ],
        paths=["scale0", "scale1"],
        axes=[
            Axis(name="x", type="space", unit="km"),
            Axis(name="y", type="space", unit="km"),
        ],
        scales=[(4, 4), (8, 8)],
        translations=[(2, 2), (4, 4)],
        name="new_image_test",
        multiscale_type="local mean",
        metadata={"key": "val"},
        global_scale=(-1, 1),
        global_translation=(10, 10),
    )


def test_datasets(example_image: Image) -> None:
    assert example_image.datasets == (
        (
            Dataset(
                path="scale0",
                coordinateTransformations=(
                    VectorScale(type="scale", scale=[4.0, 4.0]),
                    VectorTranslation(type="translation", translation=[2.0, 2.0]),
                ),
            ),
            Dataset(
                path="scale1",
                coordinateTransformations=(
                    VectorScale(type="scale", scale=[8.0, 8.0]),
                    VectorTranslation(type="translation", translation=[4.0, 4.0]),
                ),
            ),
        ),
    )


def test_new_image_wrong_transforms() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Length of 'translations' (1) does not match length of 'paths' (2)"
        ),
    ):
        Image.new(
            array_specs=[
                ArraySpec(shape=(5, 5), chunks=(2, 2), dtype=np.uint8),
                ArraySpec(shape=(3, 3), chunks=(2, 2), dtype=np.uint8),
            ],
            paths=["scale0", "scale1"],
            axes=[
                Axis(name="x", type="space", unit="km"),
                Axis(name="y", type="space", unit="km"),
            ],
            scales=[(4, 4), (8, 8)],
            translations=[(2, 2)],
            name="new_image_test",
            multiscale_type="local mean",
            metadata={"key": "val"},
            global_scale=(-1, 1),
            global_translation=(10, 10),
        )


def test_global_transform(example_image: Image) -> None:
    model_dict = example_image.model_dump()
    assert "coordinateTransformations" in model_dict["attributes"]["multiscales"][0]


def test_no_global_transform() -> None:
    new_image = Image.new(
        array_specs=[
            ArraySpec(shape=(5, 5), chunks=(2, 2), dtype=np.uint8),
            ArraySpec(shape=(3, 3), chunks=(2, 2), dtype=np.uint8),
        ],
        paths=["scale0", "scale1"],
        axes=[
            Axis(name="x", type="space", unit="km"),
            Axis(name="y", type="space", unit="km"),
        ],
        scales=[(4, 4), (8, 8)],
        translations=[(2, 2), (4, 4)],
    )
    model_dict = new_image.model_dump()
    assert "coordinateTransformations" not in model_dict["attributes"]["multiscales"][0]

    new_image.model_dump(exclude_none=True)
