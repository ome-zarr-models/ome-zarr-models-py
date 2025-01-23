from typing import Literal

from pydantic import Field

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


class SpatialMapper:
    """Container class for coordinate systems and coordinate transformations."""

    coordinate_transformations: list[CoordinateTransformation] = Field(
        ..., description="List of coordinate transformations.", min_length=1
    )
    coordinate_systems: list[CoordinateSystem] = Field(
        ..., description="List of coordinate systems.", min_length=1
    )
