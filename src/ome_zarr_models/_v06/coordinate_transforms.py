import typing
from abc import ABC, abstractmethod
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
    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        """Apply transform a single point."""

    @abstractmethod
    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        """Apply inverse transform to a single point."""


class Identity(Transform):
    """Identity transformation."""

    type: Literal["identity"] = "identity"

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return tuple(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(point)


class MapAxis(Transform):
    """Axis mapping transform."""

    type: Literal["mapAxis"] = "mapAxis"
    mapAxis: dict[str, str]

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        # Note: no way to transform a point without axis information...
        raise NotImplementedError

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        # Note: no way to transform a point without axis information...
        raise NotImplementedError


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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        # Note: no way to transform a point without axis information...
        return tuple(p + t for p, t in zip(point, self.translation, strict=True))

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(p - t for p, t in zip(point, self.translation, strict=True))


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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return tuple(p * s for p, s in zip(point, self.scale, strict=True))

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(p / s for p, s in zip(point, self.scale, strict=True))


class Affine(Transform):
    """Affine transform."""

    type: Literal["affine"] = "affine"
    affine: tuple[tuple[float, ...], ...] | None = None
    path: str | None = None

    # TODO: add a method or property to get array either from self.affine
    # or by loading Zarr array at self.path

    # TODO: if both affine and path are given, use path

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        if self.affine is None:
            raise NotImplementedError("Not implemented when self.affine is None")

        # TODO: this is wrong - need to split up matrix multiplication and translation
        return tuple(
            sum(p * col for p, col in zip(point, row, strict=True))
            for row in self.affine
        )

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        raise NotImplementedError


class Rotation(Transform):
    """Rotation transform."""

    type: Literal["rotation"] = "rotation"
    rotation: tuple[float, ...] | None = None
    path: str | None = None

    # TODO: add a method or property to get rotation either from self.rotation
    # or by loading Zarr array at self.path

    # TODO: if both rotation and path are given, use path

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError("Transforming using a rotation not yet implemented")

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        raise NotImplementedError("Transforming using a rotation not yet implemented")


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple[Transform, ...]

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        point_tuple = tuple(point)
        for transform in self.transformations:
            point_tuple = transform.transform_point(point_tuple)
        return point_tuple

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        point_tuple = tuple(point)
        for transform in self.transformations[::-1]:
            point_tuple = transform.inverse_transform_point(point_tuple)
        return point_tuple


class Displacements(Transform):
    """Displacement field transform."""

    type: Literal["displacements"] = "displacements"
    path: str
    interpolation: str

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError(
            "Transforming using a displacement field not yet implemented"
        )

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        raise NotImplementedError(
            "Transforming using a displacement field not yet implemented"
        )


class Coordinates(Transform):
    """Coordinate field transform."""

    type: Literal["coordinates"] = "coordinates"
    path: str
    interpolation: str

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError(
            "Transforming using a coordinate field not yet implemented"
        )

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        raise NotImplementedError(
            "Transforming using a coordinate field not yet implemented"
        )


class Inverse(Transform):
    """Inverse transform."""

    type: Literal["inverseOf"] = "inverseOf"
    transform: Transform

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return self.transform.transform_point(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return self.transform.inverse_transform_point(point)


class Bijection(Transform):
    """
    An invertible transform.
    """

    type: Literal["bijection"] = "bijection"
    forward: Transform
    inverse: Transform

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return self.forward.transform_point(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return self.inverse.transform_point(point)


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
)
