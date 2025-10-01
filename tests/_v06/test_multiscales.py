import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
    Scale,
    Sequence,
    Translation,
)
from ome_zarr_models._v06.multiscales import Dataset, Multiscale

COORDINATE_SYSTEM_NAME_FOR_TESTS = "coordinate_system_name_reserved_for_tests"


def test_ensure_scale_translation() -> None:
    def _gen_multiscale(
        coordinateTransformations: tuple[CoordinateTransformation, ...],
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
                scale=[1.0, 1.0],
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (the first transformation should be a scale)
    with pytest.raises(
        ValidationError,
        match=(
            "The first transformation in `coordinateTransformations` must either "
            "be a `Scale` transform or a `Sequence`"
        ),
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                Translation(
                    translation=[1.0, 1.0],
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                ),
            )
        )

    # not ok (a tuple of > 1 transformation is not allowed, a sequence should be used
    # instead)
    with pytest.raises(
        ValidationError,
        match=r"Length of transforms \(2\) not valid. Allowed lengths are \[1\].",
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                Translation(
                    translation=[1.0, 1.0],
                    input="/0",
                    output="intermediate",  # can be anything, this case is not
                    # valid anyway
                ),
                Translation(
                    translation=[1.0, 1.0],
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
                        scale=[1.0, 1.0],
                        input=None,
                        output=None,
                    ),
                    Translation(
                        translation=[1.0, 1.0],
                        input=None,
                        output=None,
                    ),
                ),
                input="/0",
                output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
            ),
        )
    )

    # not ok (the scale and translations have different dimensionalities)
    with pytest.raises(
        ValueError,
        match="The length of the scale and translation vectors must be the same",
    ):
        _ = _gen_multiscale(
            coordinateTransformations=(
                Sequence(
                    input="/0",
                    output=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                    transformations=[
                        Scale(scale=[1.0, 1.0], input=None, output=None),
                        Translation(
                            translation=[1.0, 1.0, 2.0], input=None, output=None
                        ),
                    ],
                ),
            )
        )


def test_invalid_dimensionalities() -> None:
    # not ok (one transformation has different dimensionality than the coordinate
    # system)
    with pytest.raises(
        ValidationError,
        match=(
            "All `Dataset` instances of a `Multiscale` must have the same "
            "dimensionality. Got "
        ),
    ):
        Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(
                CoordinateSystem(
                    name="out",
                    axes=[
                        Axis(name="j"),
                        Axis(name="i"),
                    ],
                ),
            ),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=(
                        Scale(
                            scale=[1.0, 1.0, 1.0],
                            input="/0",
                            output="out",
                        ),
                    ),
                ),
                Dataset(
                    path="1",
                    coordinateTransformations=(
                        Sequence(
                            transformations=(
                                Scale(
                                    scale=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                                Translation(
                                    translation=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                            ),
                            input="/1",
                            output="out",
                        ),
                    ),
                ),
            ),
        )


def test_ensure_ordered_scales() -> None:
    with pytest.raises(
        ValidationError,
        match=r" has a lower resolution \(scales =",
    ):
        Multiscale(
            coordinateTransformations=None,
            coordinateSystems=(
                CoordinateSystem(
                    name="out",
                    axes=[
                        Axis(name="j"),
                        Axis(name="i"),
                    ],
                ),
            ),
            datasets=(
                Dataset(
                    path="0",
                    coordinateTransformations=(
                        Scale(
                            scale=[2.0, 2.0],
                            input="/0",
                            output="out",
                        ),
                    ),
                ),
                Dataset(
                    path="1",
                    coordinateTransformations=(
                        Sequence(
                            transformations=(
                                Scale(
                                    scale=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                                Translation(
                                    translation=[1.0, 1.0],
                                    input=None,
                                    output=None,
                                ),
                            ),
                            input="/1",
                            output="out",
                        ),
                    ),
                ),
            ),
        )
