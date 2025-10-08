import typing
from abc import ABC, abstractmethod
from typing import Literal, Self, TypeVar

from pydantic import Field, JsonValue, field_validator, model_validator

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator

TPoint = tuple[float, ...]


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


class Transform(BaseAttrs, ABC):
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

    @abstractmethod
    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        """Apply transform a single point."""

    @abstractmethod
    def get_inverse(self) -> "Transform":
        """Inverse of this transform."""

    @property
    def _inverse_kwargs(self) -> dict[str, str | None]:
        """Common keyword arguments for constructing inverse transforms"""
        return {
            "input": self.output,
            "output": self.input,
            "name": f"{self.name}_inverse",
        }


class Identity(Transform):
    """Identity transformation."""

    type: Literal["identity"] = "identity"

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(point)

    def get_inverse(self) -> "Identity":
        return Identity(**self._inverse_kwargs)


class MapAxis(Transform):
    """Axis mapping transform."""

    type: Literal["mapAxis"] = "mapAxis"
    mapAxis: dict[str, str]

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        # Note: no way to transform a point without axis information...
        raise NotImplementedError

    def get_inverse(self) -> "MapAxis":
        raise NotImplementedError


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

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.translation is None and self.path is None:
            raise ValueError("One of 'translation' or 'path' must be given")
        return self

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(p + t for p, t in zip(point, self.translation_vector, strict=True))

    def get_inverse(self) -> "Translation":
        return Translation(
            **self._inverse_kwargs,
            translation=tuple(-t for t in self.translation_vector),
        )


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

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.scale is None and self.path is None:
            raise ValueError("One of 'scale' or 'path' must be given")
        return self

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(p * s for p, s in zip(point, self.scale_vector, strict=True))

    def get_inverse(self) -> "Scale":
        return Scale(
            **self._inverse_kwargs,
            scale=tuple(1 / s for s in self.scale_vector),
        )


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

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.affine is None and self.path is None:
            raise ValueError("One of 'affine' or 'path' must be given")
        return self

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        if self.affine is None:
            raise NotImplementedError("Not implemented when self.affine is None")
        if len(point) != len(self.affine):
            raise ValueError(
                f"Dimensionality of point ({len(point)}) does not match "
                f"dimensionality of transform ({len(self.affine)})"
            )
        point_tuple = tuple(point)
        matrix = [row[:-1] for row in self.affine]
        translation = [row[-1] for row in self.affine]
        point_out = [0.0 for _ in point_tuple]

        for i in range(len(point_out)):
            point_out[i] = sum(m * p for m, p in zip(matrix[i], point, strict=True))
            point_out[i] += translation[i]

        return tuple(point_out)

    def get_inverse(self) -> "Affine":
        raise NotImplementedError

    _TAffine = TypeVar("_TAffine", bound=tuple[tuple[float, ...], ...] | None)

    @field_validator("affine", mode="after")
    @classmethod
    def _validate_affine(cls, affine: _TAffine) -> _TAffine:
        if affine is None:
            return affine

        row_lens = [len(row) for row in affine]
        if not all(r == row_lens[0] for r in row_lens[1:]):
            raise ValueError(
                f"Row lengths in affine matrix ({row_lens}) are not all equal."
            )

        return affine


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

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.rotation is None and self.path is None:
            raise ValueError("One of 'rotation' or 'path' must be given")
        return self

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        raise NotImplementedError("Transforming using a rotation not yet implemented")

    def get_inverse(self) -> "Rotation":
        raise NotImplementedError


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple["AnyTransform", ...]

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        point_tuple = tuple(point)
        for transform in self.transformations:
            point_tuple = transform.transform_point(point_tuple)
        return point_tuple

    def get_inverse(self) -> "Sequence":
        return Sequence(
            **self._inverse_kwargs,
            transformations=tuple(t.get_inverse() for t in self.transformations[::-1]),
        )


class Displacements(Transform):
    """Displacement field transform."""

    type: Literal["displacements"] = "displacements"
    path: str
    interpolation: str

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        raise NotImplementedError(
            "Transforming using a displacement field not yet implemented"
        )

    def get_inverse(self) -> "Displacements":
        raise NotImplementedError(
            "Transforming using a displacement field not yet implemented"
        )


class Coordinates(Transform):
    """Coordinate field transform."""

    type: Literal["coordinates"] = "coordinates"
    path: str
    interpolation: str

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        raise NotImplementedError(
            "Transforming using a coordinate field not yet implemented"
        )

    def get_inverse(self) -> "Coordinates":
        raise NotImplementedError(
            "Transforming using a coordinate field not yet implemented"
        )


class Inverse(Transform):
    """Inverse transform."""

    type: Literal["inverseOf"] = "inverseOf"
    transform: "AnyTransform"

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return self.transform.transform_point(point)

    def get_inverse(self) -> "Inverse":
        return Inverse(**self._inverse_kwargs, transform=self.transform.get_inverse())


class Bijection(Transform):
    """
    An invertible transform.
    """

    type: Literal["bijection"] = "bijection"
    forward: "AnyTransform"
    inverse: "AnyTransform"

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return self.forward.transform_point(point)

    def get_inverse(self) -> "Bijection":
        return Bijection(
            **self._inverse_kwargs, forward=self.inverse, inverse=self.forward
        )


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
