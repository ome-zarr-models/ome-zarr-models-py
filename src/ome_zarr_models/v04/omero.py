from typing import Annotated

from pydantic import StringConstraints

from ome_zarr_models.base import Base

__all__ = ["Window", "Channel", "Omero"]


class Window(Base):
    """
    A single window.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/#omero-md.
    """

    max: float
    min: float
    start: float
    end: float


_RGBHexConstraint = StringConstraints(pattern=r"[0-9a-fA-F]{6}")


class Channel(Base):
    """
    Model for an element of `Omero.channels`.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/#omero-md
    """

    color: Annotated[str, _RGBHexConstraint]
    window: Window


class Omero(Base):
    """
    omero model.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/#omero-md
    """

    channels: list[Channel]
