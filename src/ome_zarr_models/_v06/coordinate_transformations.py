from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ome_zarr_models._v06.axes import Axes
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator

# to add to __all__:
# "PathScale",  # TODO: not supported yet
# "PathTranslation",  # TODO: not supported yet
__all__ = [
    "CoordinateSystem",
    "Identity",
    "ScaleTransform",
    "SequenceTransform",
    "TranslationTransform",
    "VectorScale",
    "VectorTransform",
    "VectorTranslation",
]


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


class VectorScale(CoordinateTransformationBase):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale)


class VectorTranslation(CoordinateTransformationBase):
    """Translation transformation."""

    type: Literal["translation"] = "translation"
    translation: list[float]

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation)


class SequenceTransform(CoordinateTransformationBase):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: list[CoordinateTransformation]


CoordinateTransformation = (
    Identity | VectorScale | VectorTranslation | SequenceTransform
)
ScaleTransform = VectorScale  # | PathScale # to be added
TranslationTransform = VectorTranslation  # | PathTranslation # to be added
VectorTransform = VectorScale | VectorTranslation
