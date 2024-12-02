"""
For reference, see the [omero section of the OME-zarr specification](https://ngff.openmicroscopy.org/0.4/#omero-md).
"""

from typing import Annotated

from pydantic import StringConstraints

from ome_zarr_models.base import Base

__all__ = ["Channel", "Omero", "Window"]


class Window(Base):
    """
    A single window.
    """

    max: float
    min: float
    start: float
    end: float


_RGBHexConstraint = StringConstraints(pattern=r"[0-9a-fA-F]{6}")


class Channel(Base):
    """
    A single omero channel.
    """

    color: Annotated[str, _RGBHexConstraint]
    window: Window


class Omero(Base):
    """
    omero model.
    """

    channels: list[Channel]
