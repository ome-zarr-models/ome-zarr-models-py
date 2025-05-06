import pydantic_core
import pytest
from pydantic import ValidationError

from ome_zarr_models._rfc5_transforms.axes import Axis
from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformationType,
    Scale,
    Sequence,
    Translation,
)
from ome_zarr_models._rfc5_transforms.multiscales import Dataset, Multiscale
from tests._rfc5_transforms.conftest import (
    COORDINATE_SYSTEM_NAME_FOR_TESTS,
)


def test_ensure_scale_translation():
    def _gen_multiscale(
        coordinateTransformations: tuple[CoordinateTransformationType],
    ) -> Multiscale:
        extra_cs = CoordinateSystem(
            name=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            axes=[
                Axis(name="j"),
                Axis(name="i"),
            ],
        )
        return Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(extra_cs,),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=coordinateTransformations,
                ),
            ),
        )

    # ok (a single scale transformation)
    _ = _gen_multiscale(
        coordinateTransformations=(
            Scale(
                scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (the first transformation should be a scale)
    with pytest.raises(ValidationError):
        _ = _gen_multiscale(
            coordinateTransformations=(
                Translation(
                    translation=[1.0, 1.0, 0.5, 0.5, 0.5],
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )

    # not ok (a tuple of > 1 transformation is not allowed, a sequence should be used
    # instead)
    with pytest.raises(ValidationError):
        _ = _gen_multiscale(
            coordinateTransformations=(
                Translation(
                    translation=[1.0, 1.0, 0.5, 0.5, 0.5],
                    input="/0",
                    output="intermediate",  # can be anything, this case is not
                    # valid anyway
                ),
                Translation(
                    translation=[1.0, 1.0, 0.5, 0.5, 0.5],
                    input="intermediate",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )

    # ok (a sequence of a scale and a translation)
    _ = _gen_multiscale(
        coordinateTransformations=(
            Sequence(
                transformations=(
                    Scale(
                        scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                        input=None,
                        output=None,
                    ),
                    Translation(
                        translation=[1.0, 1.0, 0.5, 0.5, 0.5],
                        input=None,
                        output=None,
                    ),
                ),
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (it's a sequence but not of a scale and a translation)
    try:
        _ = _gen_multiscale(
            coordinateTransformations=(
                Sequence(
                    transformations=(
                        Scale(
                            scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                            input=None,
                            output=None,
                        ),
                        Scale(
                            scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                            input=None,
                            output=None,
                        ),
                    ),
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )
    except pydantic_core.ValidationError as e:
        assert "1 validation error for Dataset" in str(e)

    # not ok (a sequence of a scale and a translation, but the dimensions do not match)
    try:
        _ = _gen_multiscale(
            coordinateTransformations=(
                Sequence(
                    transformations=(
                        Scale(
                            scale=[1.0, 1.0, 0.5, 0.5, 0.5],
                            input=None,
                            output=None,
                        ),
                        Translation(
                            translation=[1.0],
                            input=None,
                            output=None,
                        ),
                    ),
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )
    except pydantic_core.ValidationError as e:
        assert "1 validation error for Dataset" in str(e)
