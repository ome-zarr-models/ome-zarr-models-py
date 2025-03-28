from typing import Annotated, Literal

from pydantic import Field, field_validator

from ome_zarr_models._rfc5_transforms.axes import Axes
from ome_zarr_models._utils import duplicates
from ome_zarr_models.base import BaseAttrs


class CoordinateSystem(BaseAttrs):
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


class CoordinateTransformation(BaseAttrs):
    type: str
    input: str
    output: str


class Identity(CoordinateTransformation):
    """Identity transformation."""

    type: Literal["identity"] = "identity"


class Scale(CoordinateTransformation):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale)


CoordinateTransformationType = Annotated[Scale | Identity, Field(discriminator="type")]
