from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ome_zarr_models._rfc5_transforms.axes import Axes
from ome_zarr_models._rfc5_transforms.base import BaseOMEAttrs
from ome_zarr_models._utils import duplicates


class CoordinateSystem(BaseOMEAttrs):
    name: str
    axes: Axes

    @field_validator("name")
    def name_must_not_be_empty(cls, value: str) -> str:
        if value == "":
            raise ValueError("name must be a non-empty string")
        return value

    @field_validator("axes")
    def axes_must_not_be_empty(cls, value: Axes) -> Axes:
        if len(value) == 0:
            raise ValueError("axes must contain at least one axis")
        return value

    # TODO: add tests
    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_unique_axis_names(cls, axes: Axes) -> Axes:
        """
        Ensures that the names of the axes are unique.
        """
        name_dupes = duplicates(a.name for a in axes)
        if len(name_dupes) > 0:
            msg = (
                f"Axis names must be unique. Axis names {tuple(name_dupes.keys())} are "
                "repeated."
            )
            raise ValueError(msg)
        return axes


class CoordinateTransformation(BaseOMEAttrs):
    # TODO: extend this as we incorporate more types of transformation
    type: Literal["identity", "scale"]
    input: str
    output: str


class Identity(CoordinateTransformation):
    """Identity transformation."""

    type: Literal["identity"]


class Scale(CoordinateTransformation):
    """Scale transformation."""

    type: Literal["scale"]
    scale: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale)


# TODO: remove this class! the validation functions should be part of multiscale
# TODO: remove the test using this class and replace it with a test for multiscale
class SpatialMapper(BaseOMEAttrs):
    """Container class for coordinate systems and coordinate transformations."""

    coordinateSystems: list[CoordinateSystem] = Field(
        ..., description="List of coordinate systems.", min_length=1
    )
    coordinateTransformations: list[CoordinateTransformation] = Field(
        ..., description="List of coordinate transformations.", min_length=1
    )

    @model_validator(mode="after")
    def check_cs_input_output(self) -> Self:
        """Check input and output for each coordinate system.

        The input and output must either be a path relative to the current file in the
        zarr store or must be a name that is present in the list of coordinate systems.
        """
        cs_names = {cs.name for cs in self.coordinateSystems}

        # check input
        for transformation in self.coordinateTransformations:
            # TODO: add support for the input coordinate system being equal to the path
            #  of the array data. See more:
            # https://imagesc.zulipchat.com/#narrow/channel/469152-ome-zarr-models-py/topic/validating.20paths
            if transformation.input not in cs_names:
                raise ValueError(
                    "Invalid input in coordinate transformation: "
                    f"{transformation.input}. Must be one of {cs_names}."
                )

        # check output
        for transformation in self.coordinateTransformations:
            if transformation.output not in cs_names:
                raise ValueError(
                    "Invalid output in coordinate transformation: "
                    f"{transformation.output}. Must be one of {cs_names}."
                )
        return self
