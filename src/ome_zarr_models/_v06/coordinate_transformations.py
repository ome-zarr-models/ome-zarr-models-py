from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator


class CoordinateSystem(BaseAttrs):
    # Use min_length=1 to ensure name is non-empty
    name: str = Field(min_length=1)
    axes: tuple[Axis, ...] = Field(min_length=1)

    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_unique_axis_names(cls, axes: tuple[Axis, ...]) -> tuple[Axis, ...]:
        """
        Ensures that the names of the axes are unique.
        """
        unique_items_validator([a.name for a in axes])
        return axes


class CoordinateTransformationBase(BaseAttrs):
    type: str
    input: str | None = None
    output: str | None = None
    name: str | None = None

    @model_validator(mode="after")
    def _ensure_consistent_input_output(self: Self) -> Self:
        """
        Ensures that either both input and output are defined or both are omitted.
        """
        if (self.input is None) != (self.output is None):
            msg = (
                "Either both input and output must be defined or both must be omitted. "
                f"Got input={self.input} and output={self.output}."
            )
            raise ValueError(msg)
        return self


class Identity(CoordinateTransformationBase):
    """Identity transformation."""

    type: Literal["identity"] = "identity"


class Scale(CoordinateTransformationBase):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale)


class Translation(CoordinateTransformationBase):
    """Translation transformation."""

    type: Literal["translation"] = "translation"
    translation: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation)


class Sequence(CoordinateTransformationBase):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: list["CoordinateTransformation"]


CoordinateTransformation = Identity | Scale | Translation | Sequence
