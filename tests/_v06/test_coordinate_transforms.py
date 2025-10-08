import re

import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.coordinate_transforms import (
    Affine,
    Identity,
    Rotation,
    Scale,
    Transform,
    Translation,
)


@pytest.mark.parametrize("transform_cls", (Translation, Scale, Affine, Rotation))
def test_no_parameters(transform_cls: type[Transform]) -> None:
    # Check that errors are raised with classes that require either parameters,
    # OR paths to a Zarr array with those parameters.
    with pytest.raises(ValidationError, match=r"One of .* or 'path' must be given"):
        transform_cls()  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "transform, expected_point",
    (
        (Identity(), (0, 1, 2)),
        (Translation(translation=(3.2, 10.2, 7.5)), (3.2, 11.2, 9.5)),
        (Scale(scale=(1, 0.5, 2)), (0, 0.5, 4)),
        (Affine(affine=((1, 0, 0, 10), (0, 1, 0, -4), (0, 0, 1, 2))), (10, -3, 4)),
    ),
)
def test_transform_point(
    transform: Transform, expected_point: tuple[int, int, int]
) -> None:
    """
    Test transforming a single point.
    """
    actual_point = transform.transform_point((0, 1, 2))
    assert actual_point == expected_point


@pytest.mark.parametrize(
    "transform, expected_point",
    (
        (Identity(), (0, 1, 2)),
        (Translation(translation=(3.2, 10.2, 7.5)), (-3.2, -9.2, -5.5)),
        (Scale(scale=(1, 0.5, 2)), (0, 2, 1)),
    ),
)
def test_inverse_transform_point(
    transform: Transform, expected_point: tuple[int, int, int]
) -> None:
    """
    Test transforming a single point.
    """
    actual_point = transform.get_inverse().transform_point((0, 1, 2))
    assert actual_point == expected_point


def test_invalid_affine() -> None:
    with pytest.raises(
        ValidationError,
        match=re.escape("Row lengths in affine matrix ([1, 2]) are not all equal."),
    ):
        Affine(affine=((1,), (1, 2)))


def test_affine_dimension_mismatch() -> None:
    t = Affine(affine=((1, 0), (0, 1)))
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Dimensionality of point (1) does not match dimensionality of transform (2)"
        ),
    ):
        t.transform_point((1,))
