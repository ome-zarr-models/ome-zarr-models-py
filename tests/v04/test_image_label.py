import pytest
from pydantic import ValidationError

from ome_zarr_models.v04.image_label_types import (
    Color,
    Label,
    Property,
    Source,
)
from tests.v04.conftest import read_in_json


def test_image_label_example_json() -> None:
    model = read_in_json(json_fname="image_label_example.json", model_cls=Label)

    assert model == Label(
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
