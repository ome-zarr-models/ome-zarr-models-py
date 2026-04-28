import pytest

from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    CoordinateSystemIdentifier,
    Identity,
    Scale,
    Transform,
)
from ome_zarr_models._v06.multiscales import Dataset, Multiscale

COORDINATE_SYSTEM_NAME_FOR_TESTS = "coordinate_system_name_reserved_for_tests"


def _gen_dataset(
    output_coordinate_system: str,
    scale_factors: list[float],
    path: str = "0",
) -> Dataset:
    return Dataset(
        path=path,
        coordinateTransformations=(
            Scale(
                scale=scale_factors,
                input=CoordinateSystemIdentifier(path=f"{path}"),
                output=CoordinateSystemIdentifier(name=output_coordinate_system),
            ),
        ),
    )


def wrap_coordinate_transformations_and_systems_into_multiscale(
    coordinate_systems: tuple[CoordinateSystem, ...],
    coordinate_transformations: tuple[Transform, ...],
) -> Multiscale:
    extra_cs = CoordinateSystem(
        name=COORDINATE_SYSTEM_NAME_FOR_TESTS,
        axes=[
            Axis(name="j"),
            Axis(name="i"),
        ],
    )
    return Multiscale(
        coordinateTransformations=coordinate_transformations,
        coordinateSystems=(*coordinate_systems, extra_cs),
        datasets=(
            _gen_dataset(
                output_coordinate_system=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                scale_factors=[1.0] * len(extra_cs.axes),
            ),
        ),
    )


def test_coordinate_system_name_not_empty() -> None:
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        CoordinateSystem(name="", axes=[Axis(name="x")])


def test_coordinate_system_axes_not_empty() -> None:
    with pytest.raises(
        ValueError, match="Tuple should have at least 1 item after validation"
    ):
        CoordinateSystem(name="test", axes=[])


def test_coordinate_system_axes_unique_names() -> None:
    with pytest.raises(ValueError, match="Duplicate values found in "):
        CoordinateSystem(
            name="test",
            axes=[Axis(name="x"), Axis(name="y"), Axis(name="x")],
        )


def test_input_output_coordinate_system_valid_for_transformation() -> None:
    axis_names = ["a", "b", "c"]
    cs_names = ["in", "out", "other"]
    axes = [Axis(name=i) for i in axis_names]
    csystems = tuple([CoordinateSystem(name=i, axes=axes) for i in cs_names])
    invalid_input = (
        Identity(
            input=CoordinateSystemIdentifier(name="not_working"),
            output=CoordinateSystemIdentifier(name="out"),
        ),
    )
    invalid_output = (
        Identity(
            input=CoordinateSystemIdentifier(name="in"),
            output=CoordinateSystemIdentifier(name="not_working"),
        ),
    )
    working_transformation = (
        Identity(
            input=CoordinateSystemIdentifier(name="in"),
            output=CoordinateSystemIdentifier(name="out"),
        ),
    )

    with pytest.raises(ValueError, match="Invalid input in coordinate transformation"):
        wrap_coordinate_transformations_and_systems_into_multiscale(
            coordinate_systems=csystems, coordinate_transformations=invalid_input
        )

    with pytest.raises(ValueError, match="Invalid output in coordinate transformation"):
        wrap_coordinate_transformations_and_systems_into_multiscale(
            coordinate_systems=csystems, coordinate_transformations=invalid_output
        )

    wrap_coordinate_transformations_and_systems_into_multiscale(
        coordinate_systems=csystems, coordinate_transformations=working_transformation
    )


def test_coordinate_system_input_output_dimensionality() -> None:
    # both input and output are None (valid)
    ct = Identity(input=None, output=None)
    assert ct.input is None and ct.output is None

    # both input and output are defined (valid)
    ct = Identity(
        input=CoordinateSystemIdentifier(name="a"),
        output=CoordinateSystemIdentifier(name="b"),
    )
    assert ct.input is not None and ct.output is not None
    assert ct.input.name == "a" and ct.output.name == "b"

    with pytest.raises(
        ValueError,
        match="Either both input and output must be defined or both must be omitted",
    ):
        Identity(input=CoordinateSystemIdentifier(name="a"), output=None)

    # only output is defined (invalid)
    with pytest.raises(
        ValueError,
        match="Either both input and output must be defined or both must be omitted",
    ):
        Identity(input=None, output=CoordinateSystemIdentifier(name="b"))
