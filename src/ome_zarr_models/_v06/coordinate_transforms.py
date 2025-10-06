import typing
from abc import ABC, abstractmethod
from typing import Annotated, Literal, Self, TypeVar

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
    def get_inverse(self) -> "Transform":
        """
        Inverse of this transform.

        Raises
        ------
        NotImplementedError
            If this the inverse for this transform is not yet implemented.
        """

    @abstractmethod
    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        """Apply transform a single point."""

    @abstractmethod
    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        """Apply inverse transform to a single point."""

    @property
    def _inverse_name(self) -> str | None:
        if self.name is None:
            return None
        return f"{self.name}_inverse"

    @property
    def _short_name(self) -> str:
        return self.type


class Identity(Transform):
    """Identity transformation."""

    type: Literal["identity"] = "identity"

    def get_inverse(self) -> "Identity":
        return Identity(input=self.output, output=self.input, name=self._inverse_name)

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return tuple(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(point)


class MapAxis(Transform):
    """Axis mapping transform."""

    type: Literal["mapAxis"] = "mapAxis"
    mapAxis: tuple[int, ...]

    @property
    def ndim(self) -> int:
        return len(self.mapAxis)

    def get_inverse(self) -> "MapAxis":
        return MapAxis(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            mapAxis=tuple([self.mapAxis.index(i) for i in range(self.ndim)]),
        )

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
    translation: tuple[float, ...] | None = None
    path: str | None = None

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        return len(self.translation_vector)

    def get_inverse(self) -> "Translation":
        return Translation(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            translation=tuple([-i for i in self.translation_vector]),
        )

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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        # Note: no way to transform a point without axis information...
        return tuple(p + t for p, t in zip(point, self.translation_vector, strict=True))

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(p - t for p, t in zip(point, self.translation_vector, strict=True))


class Scale(Transform):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: tuple[float, ...] | None = None
    path: str | None = None

    def get_inverse(self) -> "Scale":
        return Scale(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            scale=tuple([1 / i for i in self.scale_vector]),
        )

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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return tuple(p * s for p, s in zip(point, self.scale_vector, strict=True))

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return tuple(p / s for p, s in zip(point, self.scale_vector, strict=True))


class Affine(Transform):
    """Affine transform."""

    type: Literal["affine"] = "affine"
    affine: tuple[tuple[float, ...], ...] | None = None
    path: str | None = None

    @property
    def ndim(self) -> int:
        return len(self.affine_matrix)

    def get_inverse(self) -> "Affine":
        raise NotImplementedError

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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
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

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
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

    def get_inverse(self) -> "Rotation":
        raise NotImplementedError

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

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError("Transforming using a rotation not yet implemented")

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        raise NotImplementedError("Transforming using a rotation not yet implemented")


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple["AnyTransform", ...]

    def get_inverse(self) -> "Sequence":
        return Sequence(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            transformations=(t.get_inverse() for t in self.transformations[::-1]),
        )

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

    def add_transform(self, transform: "AnyTransform") -> "Sequence":
        """
        Create a new sequence by adding a transform to the end of this one.
        """
        return self.model_copy(
            update={"transformations": (*self.transformations, transform)}
        )

    @property
    def _short_name(self) -> str:
        return f"sequence[{', '.join([t._short_name for t in self.transformations])}]"


class Displacements(Transform):
    """Displacement field transform."""

    type: Literal["displacements"] = "displacements"
    path: str
    interpolation: str

    def get_inverse(self) -> "Displacements":
        raise NotImplementedError

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

    def get_inverse(self) -> "Coordinates":
        raise NotImplementedError

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
    transformation: "AnyTransform"

    def get_inverse(self) -> "Coordinates":
        raise NotImplementedError

    @property
    def _short_name(self) -> str:
        return f"inverseOf[{self.transformation._short_name}]"

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return self.transformation.transform_point(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return self.transform.inverse_transform_point(point)


class Bijection(Transform):
    """
    An invertible transform.
    """

    type: Literal["bijection"] = "bijection"
    forward: "AnyTransform"
    inverse: "AnyTransform"

    def get_inverse(self) -> "Bijection":
        return Bijection(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            forward=self.inverse,
            inverse=self.forward,
        )

    @property
    def _short_name(self) -> str:
        return f"bijection[{self.forward._short_name}]"

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        return self.forward.transform_point(point)

    def inverse_transform_point(
        self, point: typing.Sequence[float]
    ) -> tuple[float, ...]:
        return self.inverse.transform_point(point)


class ByDimension(Transform):
    """
    A transform that operates on a subset of dimensions.
    """

    type: Literal["byDimension"] = "byDimension"
    transformations: tuple["AnyTransform", ...]

    def get_inverse(self) -> "ByDimension":
        raise NotImplementedError

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError


AnyTransform = Annotated[
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
    | ByDimension,
    Field(discriminator="type"),
]
