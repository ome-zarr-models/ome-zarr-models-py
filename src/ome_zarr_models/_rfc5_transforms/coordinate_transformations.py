from typing import Literal
from typing_extensions import Self
from pydantic import Field, model_validator, BaseModel
from ome_zarr_models.common.axes import Axes
from ome_zarr_models.base import BaseAttrs


class CoordinateSystem(BaseAttrs):
    name: str
    axes: Axes


class CoordinateTransformation(BaseAttrs):
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


# TODO: agree on the name of this class
class SpatialMapper(BaseModel):
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

        The input and output must either be a path relative to the current file in the zarr store
        or must be a name that is present in the list of coordinate systems.
        """
        cs_names = {cs.name for cs in self.coordinateSystems}
        for transformation in self.coordinateTransformations:
            if transformation.output not in cs_names:
                raise ValueError(f"Invalid output in coordinate transformation: {transformation.output}. Must be one of"
                                 f"{', '.join(cs_names)}")
        return self
