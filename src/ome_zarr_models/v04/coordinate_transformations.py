"""
For reference, see the [coordinate transformations section of the OME-zarr specification](https://ngff.openmicroscopy.org/0.4/#trafo-md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field
from typing_extensions import Self

from ome_zarr_models.base import Base

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

__all__ = [
    "Identity",
    "Scale",
    "Translation",
]


class Transformation(Base):
    """
    Base transformation class.
    """

    type: Literal["identity", "translation", "scale"]


class Identity(Transformation):
    """
    Identity transformation.

    Notes
    -----
    Although defined in the specification, it is not allowed
    to be used anywhere.
    """

    type: Literal["identity"]


class Scale(Transformation):
    """
    Scale transformation parametrized by a vector of numbers.
    """

    type: Literal["scale"]
    scale: list[float] | str = Field(
        ...,
        description="Scale, either as a list of scaling factors "
        "or a path to such a list in a zarr array",
    )

    @classmethod
    def build(cls, data: Iterable[float]) -> Self:
        """
        Create a VectorScale from an iterable of floats.
        """
        return cls(type="scale", scale=list(data))

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        if isinstance(self.scale, list):
            return len(self.scale)
        else:
            raise NotImplementedError(
                "Getting number of dimensions from a binary array path "
                "is not implemented"
            )

    @property
    def is_path_transform(self) -> bool:
        """
        Whether this transform is parameterized by a path or not.
        """
        return isinstance(self.scale, str)


class Translation(Transformation):
    """
    Translation transformation parametrized by a vector of numbers.
    """

    type: Literal["translation"] = Field(..., description="Type")
    translation: list[float] | str = Field(
        ...,
        description="Translation, either as a 1D translation vector "
        "or a path to such a vector in a zarr array",
    )

    @classmethod
    def build(cls, data: Iterable[float]) -> Self:
        """
        Create a VectorTranslation from an iterable of floats.
        """
        return cls(type="translation", translation=list(data))

    @property
    def ndim(self) -> int:
        """
        Number of dimensions.
        """
        if isinstance(self.translation, list):
            return len(self.translation)
        else:
            raise NotImplementedError(
                "Getting number of dimensions from a binary array path "
                "is not implemented"
            )

    @property
    def is_path_transform(self) -> bool:
        """
        Whether this transform is parameterized by a path or not.
        """
        return isinstance(self.translation, str)


def _build_transforms(
    scale: Sequence[float], translation: Sequence[float] | None
) -> tuple[Scale] | tuple[Scale, Translation]:
    """
    Create a `Scale` and optionally a `Translation` from a scale and a
    translation parameter.
    """
    vec_scale = Scale.build(scale)
    if translation is None:
        return (vec_scale,)
    else:
        vec_trans = Translation.build(translation)
        return vec_scale, vec_trans
