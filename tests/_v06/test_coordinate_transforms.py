import pytest

from ome_zarr_models._v06.coordinate_transforms import (
    Identity,
    Scale,
    Transform,
    Translation,
)


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
