import pytest

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    Identity,
)
from tests._v06.conftest import (
    wrap_coordinate_transformations_and_systems_into_multiscale,
)


def test_coordinate_system_name_not_empty() -> None:
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        CoordinateSystem(name="", axes=[Axis(name="x")])


def test_coordinate_system_axes_not_empty() -> None:
    with pytest.raises(ValueError, match="Value should have at least 1 item after"):
        CoordinateSystem(name="test", axes=[])


def test_coordinate_system_axes_unique_names() -> None:
    with pytest.raises(ValueError, match="Duplicate values found in "):
        CoordinateSystem(
            name="test",
            axes=[Axis(name="x"), Axis(name="y"), Axis(name="x")],
        )


def test_coordinate_system_ndim() -> None:
    cs = CoordinateSystem(
        name="test",
        axes=[Axis(name="x"), Axis(name="y"), Axis(name="z")],
    )
    assert cs.ndim == 3


def test_input_output_coordinate_system_valid_for_transformation() -> None:
    axis_names = ["a", "b", "c"]
    cs_names = ["in", "out", "other"]
    axes = [Axis(name=i) for i in axis_names]
    csystems = tuple([CoordinateSystem(name=i, axes=axes) for i in cs_names])
    invalid_input = (Identity(input="not_working", output="out"),)
    invalid_output = (Identity(input="in", output="not_working"),)
    working_transformation = (Identity(input="in", output="out"),)

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
    ct = Identity(input="a", output="b")
    assert ct.input == "a" and ct.output == "b"

    with pytest.raises(
        ValueError,
        match="Either both input and output must be defined or both must be omitted",
    ):
        Identity(input="a", output=None)

    # only output is defined (invalid)
    with pytest.raises(
        ValueError,
        match="Either both input and output must be defined or both must be omitted",
    ):
        Identity(input=None, output="b")
