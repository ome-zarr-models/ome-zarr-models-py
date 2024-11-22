from typing import Iterable, Literal, Sequence
from typing_extensions import Self

from pydantic import Field

from ome_zarr_models.base import Base


class Identity(Base):
    """
    Model for an identity transformation.

    See https://ngff.openmicroscopy.org/0.4/#trafo-md
    """

    type: Literal["identity"]


class VectorScale(Base):
    """
    Model for a scale transformation parametrized by a vector of numbers.

    This corresponds to scale-type elements of
    `Dataset.coordinateTransformations` or
    `Multiscale.coordinateTransformations`.
    See https://ngff.openmicroscopy.org/0.4/#trafo-md
    """

    type: Literal["scale"]
    scale: list[float]

    @classmethod
    def build(cls, data: Iterable[float]) -> Self:
        """
        Create a VectorScale from an iterable of floats.
        """
        return cls(type="scale", scale=tuple(data))

    @property
    def ndim(self) -> int:
        return len(self.scale)


class PathScale(Base):
    """
    Model for a scale transformation parametrized by a path.

    This corresponds to scale-type elements of
    `Dataset.coordinateTransformations` or
    `Multiscale.coordinateTransformations`.
    See https://ngff.openmicroscopy.org/0.4/#trafo-md
    """

    type: Literal["scale"]
    path: str


class VectorTranslation(Base):
    """
    Model for a translation transformation parametrized by a vector of numbers.

    This corresponds to translation-type elements of
    `Dataset.coordinateTransformations` or
    `Multiscale.coordinateTransformations`.
    See https://ngff.openmicroscopy.org/0.4/#trafo-md
    """

    type: Literal["translation"]
    translation: list[float]

    @classmethod
    def build(cls, data: Iterable[float]) -> Self:
        """
        Create a VectorTranslation from an iterable of floats.
        """
        return cls(type="translation", translation=tuple(data))

    @property
    def ndim(self) -> int:
        return len(self.translation)


class PathTranslation(Base):
    """
    Model for a translation transformation parametrized by a path.

    This corresponds to translation-type elements of
    `Dataset.coordinateTransformations` or
    `Multiscale.coordinateTransformations`.
    See https://ngff.openmicroscopy.org/0.4/#trafo-md
    """

    type: Literal["translation"]
    translation: str


def ndim(transform: VectorScale | VectorTranslation) -> int:
    """
    Get the dimensionality of a scale or translation transform.
    """
    if hasattr(transform, "scale"):
        return len(transform.scale)
    elif hasattr(transform, "translation"):
        return len(transform.translation)
    else:
        msg = f"Cannot infer the dimensionality of {type(transform)}"
        raise TypeError(msg)


def _build_transforms(
    scale: Sequence[float], translation: Sequence[float] | None
) -> tuple[VectorScale] | tuple[VectorScale, VectorTranslation]:
    """
    Create a `VectorScale` and optionally a `VectorTranslation` from a scale and a translation
    parameter.
    """

    vec_scale = VectorScale.build(scale)
    if translation is None:
        return (vec_scale,)
    else:
        vec_trans = VectorTranslation.build(translation)
        return vec_scale, vec_trans
