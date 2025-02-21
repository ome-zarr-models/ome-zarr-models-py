from typing import Literal

from pydantic import Field, model_validator

from ome_zarr_models.base import BaseAttrs


class CoordinateSystem:
    pass


class CoordinateTransformation(BaseAttrs):
    # TODO: extend this as we incorporate more types of transformation
    type: Literal["identity"]
    input: str
    output: str


class Identity(CoordinateTransformation):
    """Identity transformation."""

    type: Literal["identity"]


# TODO: agree on the naming of this class
class SpatialMapper:
    """Container class for coordinate systems and coordinate transformations."""

    coordinate_systems: list[CoordinateSystem] = Field(
        ..., description="List of coordinate systems.", min_length=1
    )
    coordinate_transformations: list[CoordinateTransformation] = Field(
        ..., description="List of coordinate transformations.", min_length=1
    )

    @model_validator(mode="after")
    def check_cs_input_output(self):
        """Check input and output for each coordinate system.

        The input and output must either be a path relative to the top level of the zarr store
        or must be a name that is present in the list of coordinate systems.
        """
        pass
