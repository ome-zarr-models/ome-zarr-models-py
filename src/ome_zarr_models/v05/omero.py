"""
For reference, see the [omero section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#omero-md).
"""

from typing import Annotated

from pydantic import StringConstraints

from ome_zarr_models.base import BaseAttrs

__all__ = ["Channel", "Omero", "Window"]


class Window(BaseAttrs):
    """
    A single window.
    """

    max: float
    min: float
    start: float
    end: float


_RGBHexConstraint = StringConstraints(pattern=r"[0-9a-fA-F]{6}")


class Channel(BaseAttrs):
    """
    A single omero channel.
    """

    color: Annotated[str, _RGBHexConstraint]
    window: Window


class Omero(BaseAttrs):
    """
    omero model.
    """

    channels: list[Channel]
