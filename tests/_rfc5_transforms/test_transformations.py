import pytest

from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
    SpatialMapper,
)
from ome_zarr_models.common.axes import Axis
from tests._rfc5_transforms.conftest import read_in_json


def test_coordinate_system_name_not_empty() -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        CoordinateSystem(name="", axes=[Axis(name="x")])


def test_coordinate_system_axes_not_empty() -> None:
    with pytest.raises(ValueError, match="axes must contain at least one axis"):
        CoordinateSystem(name="test", axes=[])


def test_identity_transform() -> None:
    read = read_in_json(json_fname="identity.json", model_cls=SpatialMapper)
    in_memory = SpatialMapper(
        coordinateSystems=[
            CoordinateSystem(
                name="in",
                axes=[
                    Axis(name="j"),
                    Axis(name="i"),
                ],
            ),
            CoordinateSystem(
                name="out",
                axes=[
                    Axis(name="y"),
                    Axis(name="x"),
                ],
            ),
            CoordinateSystem(
                name="out2",
                axes=[
                    Axis(name="y"),
                    Axis(name="x"),
                ],
            ),
        ],
        coordinateTransformations=[
            CoordinateTransformation(type="identity", input="in", output="out")
        ],
    )
    assert read == in_memory


def test_transformation_input_output_validation() -> None:
    axis_names = ["a", "b", "c"]
    cs_names = ["in", "out", "other"]
    axes = [Axis(name=i) for i in axis_names]
    csystems = [CoordinateSystem(name=i, axes=axes) for i in cs_names]
    invalid_input = [
        CoordinateTransformation(type="identity", input="not_working", output="out")
    ]
    invalid_output = [
        CoordinateTransformation(type="identity", input="in", output="not_working")
    ]
    working_transformation = [
        CoordinateTransformation(type="identity", input="in", output="out")
    ]

    with pytest.raises(ValueError, match="Invalid input in coordinate transformation"):
        SpatialMapper(
            coordinateSystems=csystems, coordinateTransformations=invalid_input
        )

    with pytest.raises(ValueError, match="Invalid output in coordinate transformation"):
        SpatialMapper(
            coordinateSystems=csystems, coordinateTransformations=invalid_output
        )

    SpatialMapper(
        coordinateSystems=csystems, coordinateTransformations=working_transformation
    )


def test_coordinate_transformations_full_metadata() -> None:
    pass
