import re

import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.coordinate_transforms import (
    Affine,
    Bijection,
    Identity,
    MapAxis,
    Rotation,
    Scale,
    Sequence,
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
    "transform, inverse_expected",
    [
        (Identity(), Identity()),
        (MapAxis(mapAxis=(2, 0, 1)), MapAxis(mapAxis=(1, 2, 0))),
        (Translation(translation=(-1, 23)), Translation(translation=(1, -23))),
        (Scale(scale=(-1, 2, 0.5)), Scale(scale=(-1, 0.5, 2))),
        (
            Sequence(
                transformations=(
                    Scale(scale=(0.5, -2)),
                    Translation(translation=(2, -9)),
                )
            ),
            Sequence(
                transformations=(
                    Translation(translation=(-2, 9)),
                    Scale(scale=(2, -0.5)),
                )
            ),
        ),
        (
            Bijection(forward=Scale(scale=(4,)), inverse=Scale(scale=(1 / 4,))),
            Bijection(forward=Scale(scale=(1 / 4,)), inverse=Scale(scale=(4,))),
        ),
    ],
)
def test_inverse(transform: Transform, inverse_expected: Transform) -> None:
    # Manually set coordinate systems to check they're correctly swapped in inverse
    transform = transform.model_copy(
        update={"input": "input_system", "output": "output_system"}
    )
    inverse_expect = inverse_expected.model_copy(
        update={"input": "output_system", "output": "input_system"}
    )
    assert transform.get_inverse() == inverse_expect


@pytest.mark.parametrize(
    "transform, expected_point",
    (
        (Identity(), (0, 1, 2)),
        (MapAxis(mapAxis=(2, 0, 1)), (2, 0, 1)),
        (Translation(translation=(3.2, 10.2, 7.5)), (3.2, 11.2, 9.5)),
        (Scale(scale=(1, 0.5, 2)), (0, 0.5, 4)),
        (Affine(affine=((1, 0, 0, 10), (0, 1, 0, -4), (0, 0, 1, 2))), (10, -3, 4)),
        # TODO: change the rotation matrix to not the identity
        (Rotation(rotation=((1, 0, 0), (0, 1, 0), (0, 0, 1))), (0, 1, 2)),
        (
            Sequence(
                transformations=(
                    Scale(scale=(1, 0.5, 2)),
                    Translation(translation=(0, 1, 2)),
                )
            ),
            (0, 1.5, 6),
        ),
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
