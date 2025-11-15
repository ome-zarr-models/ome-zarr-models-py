import copy
import typing
from abc import ABC, abstractmethod
from typing import Annotated, Literal, Self, TypeVar

import numpy as np
from pydantic import Field, JsonValue, field_validator, model_validator

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator

TPoint = tuple[float, ...]


class NoAffineError(RuntimeError):
    """
    Exception raised when it's not possible to convert a transform to an affine.
    """


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

    Notes
    -----
    Coordinate transformations have a `transform_point` method to transform a single
    point. This only operates on a `tuple` of coordinate points, and not other objects
    that could represent points (e.g., NumPy arrays). This is a deliberate choice to
    keep the dependencies of `ome-zarr-models` slim. Other libraries are encouraged
    to implement their own coordinate transforms, and use the `transform_point` methods
    here as reference implementations to check their own implementations.
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

    @property
    @abstractmethod
    def has_inverse(self) -> bool:
        """
        True if ome-zarr models can return an inverse from `get_inverse()`.
        """

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
    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        """Apply transform a single point."""

    @abstractmethod
    def as_affine(self) -> "Affine":
        """
        Convert this transform to an equivalent affine transform.

        Raises
        ------
        NoAffineError :
            If this transform can't be converted to an affine transform.
        """

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

    @property
    def has_inverse(self) -> bool:
        return True

    def get_inverse(self) -> "Identity":
        return Identity(input=self.output, output=self.input, name=self._inverse_name)

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(point)

    def as_affine(self) -> "Affine":
        raise NoAffineError


class MapAxis(Transform):
    """Axis mapping transform."""

    type: Literal["mapAxis"] = "mapAxis"
    mapAxis: tuple[int, ...]

    @property
    def ndim(self) -> int:
        return len(self.mapAxis)

    @property
    def has_inverse(self) -> bool:
        return True

    def get_inverse(self) -> "MapAxis":
        return MapAxis(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            mapAxis=tuple([self.mapAxis.index(i) for i in range(self.ndim)]),
        )

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(point[i] for i in self.mapAxis)

    @field_validator("mapAxis", mode="after")
    @classmethod
    def check_all_axes(cls, mapAxis: tuple[int, ...]) -> tuple[int, ...]:
        if set(mapAxis) != set(range(len(mapAxis))):
            raise ValueError(
                f"Not all axes present from 0 to {len(mapAxis) - 1}: {mapAxis}"
            )
        return mapAxis

    def as_affine(self) -> "Affine":
        matrix = np.zeros((self.ndim, self.ndim))
        vector = np.zeros(self.ndim)
        for row, col in enumerate(self.mapAxis):
            matrix[row, col] = 1

        return Affine._from_matrix_vector(
            matrix=tuple(tuple(row) for row in matrix),
            vector=tuple(vector),
            input=self.input,
            output=self.output,
            name=self.name,
        )


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
    def has_inverse(self) -> bool:
        return True

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

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(p + t for p, t in zip(point, self.translation_vector, strict=True))

    def as_affine(self) -> "Affine":
        return Affine._from_matrix_vector(
            matrix=tuple(tuple(row) for row in np.identity(self.ndim)),
            vector=self.translation_vector,
            input=self.input,
            output=self.output,
            name=self.name,
        )

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.translation is None and self.path is None:
            raise ValueError("One of 'translation' or 'path' must be given")
        return self


class Scale(Transform):
    """Scale transformation."""

    type: Literal["scale"] = "scale"
    scale: tuple[float, ...] | None = None
    path: str | None = None

    @property
    def has_inverse(self) -> bool:
        return True

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

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return tuple(p * s for p, s in zip(point, self.scale_vector, strict=True))

    def as_affine(self) -> "Affine":
        matrix = np.identity(self.ndim)
        for i, scale in enumerate(self.scale_vector):
            matrix[i, i] = scale

        return Affine._from_matrix_vector(
            matrix=tuple(tuple(row) for row in matrix),
            vector=tuple(np.zeros(self.ndim)),
            input=self.input,
            output=self.output,
            name=self.name,
        )

    @model_validator(mode="after")
    def check_metadata_set(self) -> Self:
        if self.scale is None and self.path is None:
            raise ValueError("One of 'scale' or 'path' must be given")
        return self


class Affine(Transform):
    """Affine transform."""

    type: Literal["affine"] = "affine"
    affine: tuple[tuple[float, ...], ...] | None = None
    path: str | None = None

    @classmethod
    def _from_matrix_vector(
        cls,
        matrix: tuple[tuple[float, ...], ...],
        vector: typing.Sequence[float],
        input: str | None = None,
        output: str | None = None,
        name: str | None = None,
    ) -> Self:
        return cls(
            affine=tuple((*row, x) for row, x in zip(matrix, vector, strict=True)),
            input=input,
            output=output,
            name=name,
        )

    @property
    def ndim(self) -> int:
        return len(self.affine_matrix)

    @property
    def has_inverse(self) -> bool:
        return False

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

    @property
    def _matrix(self) -> list[tuple[float, ...]]:
        return [row[:-1] for row in self.affine_matrix]

    @property
    def _translation(self) -> list[float]:
        return [row[-1] for row in self.affine_matrix]

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        if len(point) != len(self.affine_matrix):
            raise ValueError(
                f"Dimensionality of point ({len(point)}) does not match "
                f"dimensionality of transform ({len(self.affine_matrix)})"
            )
        point_tuple = tuple(point)
        point_out = [0.0 for _ in point_tuple]

        for i in range(len(point_out)):
            point_out[i] = sum(
                m * p for m, p in zip(self._matrix[i], point, strict=True)
            )
            point_out[i] += self._translation[i]

        return tuple(point_out)

    def as_affine(self) -> "Affine":
        return self.model_copy()

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
    def has_inverse(self) -> bool:
        return False

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

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        rotation = copy.deepcopy(self.rotation_matrix)
        affine = tuple([(*row, 0.0) for row in rotation])
        return Affine(affine=affine).transform_point(point)

    def as_affine(self) -> "Affine":
        return Affine._from_matrix_vector(
            matrix=self.rotation_matrix,
            vector=tuple(np.zeros(self.ndim)),
            input=self.input,
            output=self.output,
            name=self.name,
        )


class Sequence(Transform):
    """Sequence transformation."""

    type: Literal["sequence"] = "sequence"
    transformations: tuple["AnyTransform", ...]

    @property
    def has_inverse(self) -> bool:
        return all(t.has_inverse for t in self.transformations)

    def get_inverse(self) -> "Sequence":
        return Sequence(
            input=self.output,
            output=self.input,
            name=self._inverse_name,
            transformations=(t.get_inverse() for t in self.transformations[::-1]),
        )

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        point_tuple = tuple(point)
        for transform in self.transformations:
            point_tuple = transform.transform_point(point_tuple)
        return point_tuple

    def add_transform(self, transform: "AnyTransform") -> "Sequence":
        """
        Create a new sequence by adding a transform to the end of this one.
        """
        return self.model_copy(
            update={"transformations": (*self.transformations, transform)}
        )

    def as_affine(self) -> "Affine":
        if not all(hasattr(t, "ndim") for t in self.transformations):
            raise NoAffineError(
                "Can't determine dimensionality of all transforms in this sequence."
            )
        ndim = self.transformations[0].ndim  # type:ignore[union-attr]
        if not all(t.ndim == ndim for t in self.transformations):  # type:ignore[union-attr]
            raise NoAffineError(
                "Not all transforms have the same dimensionality in this sequence"
            )

        matrix = np.identity(ndim)
        translation = np.zeros(ndim)
        try:
            for t in self.transformations:
                new_affine = t.as_affine()
                new_matrix = np.array(new_affine._matrix)
                matrix = new_matrix @ matrix
                translation = np.dot(new_matrix, translation) + np.array(
                    new_affine._translation
                )
        except NoAffineError as e:
            raise NoAffineError(
                "At least one transform in this sequence cannot be converted "
                "to an affine transform."
            ) from e

        return Affine._from_matrix_vector(
            matrix=matrix.tolist(), vector=translation.tolist()
        )

    @property
    def _short_name(self) -> str:
        return f"sequence[{', '.join([t._short_name for t in self.transformations])}]"


class Displacements(Transform):
    """Displacement field transform."""

    type: Literal["displacements"] = "displacements"
    path: str
    interpolation: str

    @property
    def has_inverse(self) -> bool:
        return False

    def get_inverse(self) -> "Displacements":
        raise NotImplementedError

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        raise NotImplementedError(
            "Transforming using a displacement field not yet implemented"
        )

    def as_affine(self) -> "Affine":
        raise NoAffineError


class Coordinates(Transform):
    """Coordinate field transform."""

    type: Literal["coordinates"] = "coordinates"
    path: str
    interpolation: str

    @property
    def has_inverse(self) -> bool:
        return False

    def get_inverse(self) -> "Coordinates":
        raise NotImplementedError

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        raise NotImplementedError(
            "Transforming using a coordinate field not yet implemented"
        )

    def as_affine(self) -> "Affine":
        raise NoAffineError


class Bijection(Transform):
    """
    An invertible transform.
    """

    type: Literal["bijection"] = "bijection"
    forward: "AnyTransform"
    inverse: "AnyTransform"

    @property
    def has_inverse(self) -> bool:
        return True

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

    def transform_point(self, point: typing.Sequence[float]) -> TPoint:
        return self.forward.transform_point(point)

    def as_affine(self) -> "Affine":
        raise NoAffineError


class ByDimension(Transform):
    """
    A transform that operates on a subset of dimensions.
    """

    type: Literal["byDimension"] = "byDimension"
    transformations: tuple["AnyTransform", ...]

    @property
    def has_inverse(self) -> bool:
        return False

    def get_inverse(self) -> "ByDimension":
        raise NotImplementedError

    def transform_point(self, point: typing.Sequence[float]) -> tuple[float, ...]:
        raise NotImplementedError

    def as_affine(self) -> "Affine":
        raise NoAffineError


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
    | Bijection
    | ByDimension,
    Field(discriminator="type"),
]
