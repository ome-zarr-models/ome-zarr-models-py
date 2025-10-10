from typing import Literal, Self

from pydantic import Field, JsonValue, field_validator, model_validator

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator


class Axis(BaseAttrs):
    """
    Model for an element of `Multiscale.axes`.
    """

    # Explicitly name could be any JsonValue, but implicitly it must match Zarr array
    # dimension_names which limits it to str | None

    name: str | None
    type: (
        Literal["array", "space", "time", "channel", "coordinate", "displacement"]
        | str
        | None
    ) = None
    discrete: bool | None = None
    # Unit probably intended to be str, but the spec doesn't explicitly specify
    unit: str | JsonValue | None = None
    longName: str | None = None


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

    @property
    def ndim(self) -> int:
        return len(self.axes)


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


class MapAxis(Transform):
    """Axis mapping transform."""

    type: Literal["mapAxis"] = "mapAxis"
    mapAxis: dict[str, str]


class Translation(Transform):
    """Translation transformation."""

    type: Literal["translation"] = "translation"
    translation: tuple[float, ...] | None = None
    path: str | None = None

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation_vector)

    @property
    def translation_vector(self) -> tuple[float, ...]:
        """
        Translation vector for this transform.
        """
        if self.translation is not None:
            return self.translation
        elif self.path is not None:
            raise NotImplementedError(
                "Loading translation from a Zarr array not yet implemented"
            )
        else:
            raise RuntimeError("Both self.translation and self.path are None")


class Scale(Transform):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: tuple[float, ...] | None = None
    path: str | None = None

    @property
    def scale_vector(self) -> tuple[float, ...]:
        """
        Scale vector for this transform.
        """
        if self.scale is not None:
            return self.scale
        elif self.path is not None:
            raise NotImplementedError(
                "Loading scale from a Zarr array not yet implemented"
            )
        else:
            raise RuntimeError("Both self.scale and self.path are None")

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.scale_vector)


class Affine(Transform):
    """Affine transform."""

    type: Literal["affine"] = "affine"
    affine: tuple[tuple[float, ...], ...] | None = None
    path: str | None = None

    @property
    def ndim(self) -> int:
        return len(self.affine_matrix)

    @property
    def affine_matrix(self) -> tuple[tuple[float, ...], ...]:
        if self.affine is not None:
            return self.affine
        elif self.path is not None:
            raise NotImplementedError(
                "Loading affine matrix from a Zarr array not yet implemented"
            )
        else:
            raise RuntimeError("Both self.affine and self.path are None")


class Rotation(Transform):
    """Rotation transform."""

    type: Literal["rotation"] = "rotation"
    rotation: tuple[tuple[float, ...], ...] | None = None
    path: str | None = None

    @property
    def ndim(self) -> int:
        return len(self.rotation_matrix)

    @property
    def rotation_matrix(self) -> tuple[tuple[float, ...], ...]:
        if self.rotation is not None:
            return self.rotation
        elif self.path is not None:
            raise NotImplementedError(
                "Loading rotation matrix from a Zarr array not yet implemented"
            )
        else:
            raise RuntimeError("Both self.rotation and self.path are None")


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple["AnyTransform", ...]


class Displacements(Transform):
    """Displacement field transform."""

    type: Literal["displacements"] = "displacements"
    path: str
    interpolation: str


class Coordinates(Transform):
    """Coordinate field transform."""

    type: Literal["coordinates"] = "coordinates"
    path: str
    interpolation: str


class Inverse(Transform):
    """Inverse transform."""

    type: Literal["inverseOf"] = "inverseOf"
    transform: "AnyTransform"


class Bijection(Transform):
    """
    An invertible transform.
    """

    type: Literal["bijection"] = "bijection"
    forward: "AnyTransform"
    inverse: "AnyTransform"


class ByDimension(Transform):
    """
    A transform that operates on a subset of dimensions.
    """

    type: Literal["byDimension"] = "byDimension"
    transformations: tuple["AnyTransform", ...]


AnyTransform = (
    Identity
    | MapAxis
    | Translation
    | Scale
    | Affine
    | Rotation
    | Sequence
    | Displacements
    | Coordinates
    | Inverse
    | Bijection
    | ByDimension
)
