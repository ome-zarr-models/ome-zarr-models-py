from typing import Literal

from pydantic import Field, model_validator
from ome_zarr_models.common.axes import Axes
from ome_zarr_models.base import BaseAttrs


class CoordinateSystem(BaseAttrs):
    name: str
    axes: Axes


class CoordinateTransformation(BaseAttrs):
    # TODO: extend this as we incorporate more types of transformation
    type: Literal["identity", "scale"]
    output: str
    input: str


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


# TODO: agree on the name of this class
class SpatialMapper(BaseAttrs):
    """Container class for coordinate systems and coordinate transformations."""

    coordinateSystems: list[CoordinateSystem] = Field(
        ..., description="List of coordinate systems.", min_length=1
    )
    coordinateTransformations: list[CoordinateTransformation] = Field(
        ..., description="List of coordinate transformations.", min_length=1
    )

    @model_validator(mode="after")
    def check_cs_input_output(self):
        """Check input and output for each coordinate system.

        The input and output must either be a path relative to the current file in the zarr store
        or must be a name that is present in the list of coordinate systems.
        """
        pass
