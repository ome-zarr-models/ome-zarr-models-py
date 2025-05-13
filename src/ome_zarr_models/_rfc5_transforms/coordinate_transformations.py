from __future__ import annotations

from abc import ABC
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ome_zarr_models._rfc5_transforms.axes import Axes
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator


class CoordinateSystem(BaseAttrs):
    name: str = Field(min_length=1)
    axes: Axes = Field(min_length=1)

    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_unique_axis_names(cls, axes: Axes) -> Axes:
        """
        Ensures that the names of the axes are unique.
        """
        unique_items_validator([a.name for a in axes])
        return axes


class CoordinateTransformation(BaseAttrs, ABC):
    type: str
    input: str | None
    output: str | None

    @model_validator(mode="after")
    def ensure_input_output_omitted_or_both_defined(self: Self) -> Self:
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


class Translation(CoordinateTransformation):
    """Translation transformation."""

    type: Literal["translation"] = "translation"
    translation: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation)


class Sequence(CoordinateTransformation):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: list[CoordinateTransformationType]


CoordinateTransformationType = Identity | Scale | Translation | Sequence
