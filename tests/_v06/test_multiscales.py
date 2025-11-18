import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    Scale,
    Sequence,
    Transform,
    Translation,
)
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from ome_zarr_models.common.coordinate_transformations import (
    VectorScale,
    VectorTranslation,
)
from ome_zarr_models.v05.axes import Axis as Axisv05
from ome_zarr_models.v05.multiscales import (
    Dataset as Datasetv05,
)
from ome_zarr_models.v05.multiscales import (
    Multiscale as Multiscalev05,
)

COORDINATE_SYSTEM_NAME_FOR_TESTS = "coordinate_system_name_reserved_for_tests"


@pytest.mark.skip
def test_ensure_scale_translation() -> None:
    def _gen_multiscale(
        coordinateTransformations: tuple[Transform, ...],
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


@pytest.mark.skip
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


@pytest.mark.skip
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


def test_default_coordinate_systems() -> None:
    multiscale = Multiscale(
        coordinateTransformations=None,
        coordinateSystems=(
            CoordinateSystem(
                name="an_other_system",
                axes=[
                    Axis(name="x"),
                    Axis(name="y"),
                ],
            ),
            CoordinateSystem(
                name="physical",
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
                        input="0",
                        output="out",
                    ),
                ),
            ),
        ),
    )
    assert multiscale.intrinsic_coordinate_system == CoordinateSystem(
        name="physical",
        axes=(
            Axis(name="j", type=None, discrete=None, unit=None, longName=None),
            Axis(name="i", type=None, discrete=None, unit=None, longName=None),
        ),
    )
    assert multiscale.default_coordinate_system == CoordinateSystem(
        name="an_other_system",
        axes=(
            Axis(name="x", type=None, discrete=None, unit=None, longName=None),
            Axis(name="y", type=None, discrete=None, unit=None, longName=None),
        ),
    )


def test_from_v05() -> None:
    ms = Multiscalev05(
        axes=(
            Axisv05(name="x", type="space", unit="meter"),
            Axisv05(name="y", type="space", unit="meter"),
        ),
        datasets=(
            Datasetv05(
                path="0",
                coordinateTransformations=(
                    VectorScale(type="scale", scale=[2, -4]),
                    VectorTranslation(type="translation", translation=[5, 3]),
                ),
            ),
        ),
        coordinateTransformations=(VectorScale(type="scale", scale=[6, 3]),),
        metadata={"key": "value"},
        name="my_multiscale",
        type="my_type",
    )
    assert Multiscale.from_v05(
        ms,
        intrinsic_system_name="intrinsic",
        top_level_system=CoordinateSystem(
            name="top_level", axes=(Axis(name="x"), Axis(name="y"))
        ),
    ) == Multiscale(
        coordinateSystems=(
            CoordinateSystem(
                name="intrinsic",
                axes=(
                    Axis(
                        name="x",
                        type="space",
                        discrete=None,
                        unit="meter",
                        longName=None,
                    ),
                    Axis(
                        name="y",
                        type="space",
                        discrete=None,
                        unit="meter",
                        longName=None,
                    ),
                ),
            ),
            CoordinateSystem(
                name="top_level",
                axes=(
                    Axis(name="x", type=None, discrete=None, unit=None, longName=None),
                    Axis(name="y", type=None, discrete=None, unit=None, longName=None),
                ),
            ),
        ),
        datasets=(
            Dataset(
                path="0",
                coordinateTransformations=(
                    Sequence(
                        type="sequence",
                        input="0",
                        output="intrinsic",
                        name=None,
                        transformations=(
                            Scale(
                                type="scale",
                                input=None,
                                output=None,
                                name=None,
                                scale=(2.0, -4.0),
                                path=None,
                            ),
                            Translation(
                                type="translation",
                                input=None,
                                output=None,
                                name=None,
                                translation=(5.0, 3.0),
                                path=None,
                            ),
                        ),
                    ),
                ),
            ),
        ),
        coordinateTransformations=(
            Scale(
                type="scale",
                input="intrinsic",
                output="top_level",
                name=None,
                scale=(6.0, 3.0),
                path=None,
            ),
        ),
        metadata={"key": "value"},
        name="my_multiscale",
        type="my_type",
    )
