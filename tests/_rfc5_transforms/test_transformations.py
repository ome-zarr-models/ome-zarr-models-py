import pytest

from ome_zarr_models._rfc5_transforms.axes import Axis
from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    Identity,
)
from tests._rfc5_transforms.conftest import (
    wrap_coordinate_transformations_and_systems_into_multiscale,
)


def test_coordinate_system_name_not_empty() -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        CoordinateSystem(name="", axes=[Axis(name="x")])


def test_coordinate_system_axes_not_empty() -> None:
    with pytest.raises(ValueError, match="axes must contain at least one axis"):
        CoordinateSystem(name="test", axes=[])


def test_transformation_input_output_validation() -> None:
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


def test_coordinate_transformations_full_metadata() -> None:
    pass
