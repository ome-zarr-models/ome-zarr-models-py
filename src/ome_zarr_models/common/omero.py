from typing import Annotated

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import RGBHexConstraint

__all__ = ["Channel", "Omero", "Window"]


class Window(BaseAttrs):
    """
    A single window.
    """

    max: float
    min: float
    start: float
    end: float


class Channel(BaseAttrs):
    """
    A single omero channel.
    """

    color: Annotated[str, RGBHexConstraint]
    window: Window


class Omero(BaseAttrs):
    """
    omero model.
    """

    channels: list[Channel]
