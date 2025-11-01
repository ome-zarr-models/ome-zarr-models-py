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
