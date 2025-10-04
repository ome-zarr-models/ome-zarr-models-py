from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator


class CoordinateSystem(BaseAttrs):
    """
    Model of a coordinate system.
    """

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


class Transform(BaseAttrs):
    """
    Model of a coordinate transformation.
    """

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


class Identity(Transform):
    """Identity transformation."""

    type: Literal["identity"] = "identity"


class Scale(Transform):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: tuple[float, ...]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale)


class Translation(Transform):
    """Translation transformation."""

    type: Literal["translation"] = "translation"
    translation: tuple[float, ...]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation)


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple["AnyTransform", ...]


AnyTransform = Identity | Scale | Translation | Sequence
