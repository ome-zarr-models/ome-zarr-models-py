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
