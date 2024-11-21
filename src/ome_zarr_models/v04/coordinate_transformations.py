from typing import Literal

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
    scale: list[float] = Field(..., min_length=2)


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
    translation: list[float] = Field(..., min_length=2)


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
