import pytest
from pydantic import ValidationError
from zarr.abc.store import Store

from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.coordinate_transformations import VectorScale
from ome_zarr_models.v04.image_label import ImageLabel, ImageLabelAttrs
from ome_zarr_models.v04.image_label_types import (
    Color,
    Label,
    Property,
    Source,
)
from ome_zarr_models.v04.multiscales import Dataset, Multiscale
from tests.conftest import UnlistableStore
from tests.v04.conftest import json_to_zarr_group


def test_image_label_example_json(store: Store) -> None:
    if isinstance(store, UnlistableStore):
        pytest.xfail("ImageLabel does not work on unlistable stores")

    zarr_group = json_to_zarr_group(json_fname="image_label_example.json", store=store)
    zarr_group.create_array("0", shape=(1, 1, 1, 1, 1), dtype="uint8")
    ome_group = ImageLabel.from_zarr(zarr_group)

    assert ome_group.attributes == ImageLabelAttrs(
        image_label=Label(
            colors=(
                Color(label_value=1, rgba=(255, 255, 255, 255)),
                Color(label_value=4, rgba=(0, 255, 255, 128)),
            ),
            properties=(
                Property(label_value=1, area=1200, cls="foo"),
                Property(label_value=4, area=1650),
            ),
            source=Source(image="../../"),
            version="0.4",
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
                ),
                version="0.4",
                coordinateTransformations=(
                    VectorScale(type="scale", scale=[0.1, 1.0, 1.0, 1.0, 1.0]),
                ),
                metadata={
                    "description": "abc",
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


def test_invalid_label() -> None:
    """
    > Each color object MUST contain the label-value key whose value MUST be an integer
    > specifying the pixel value for that label
    """
    with pytest.raises(ValidationError, match="Input should be a valid integer"):
        Color(label_value="abc", rgba=(255, 255, 255, 255))


def test_invalid_rgba() -> None:
    """
    >  MUST be an array of four integers between 0 and 255 [uint8, uint8, uint8, uint8]
    > specifying the label color as RGBA
    """
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 255"
    ):
        Color(label_value=1, rgba=(255, 255, 3412, 255))


def test_default_source() -> None:
    """
    Check that default image source is '../../'
    """
    attrs = Label(
        colors=(
            Color(label_value=1, rgba=(255, 255, 255, 255)),
            Color(label_value=4, rgba=(0, 255, 255, 128)),
        ),
        properties=(
            Property(label_value=1, area=1200, cls="foo"),
            Property(label_value=4, area=1650),
        ),
        source={"planet": "Mars"},
        version="0.4",
    )
    assert attrs.source is not None
    assert attrs.source.image == "../../"
