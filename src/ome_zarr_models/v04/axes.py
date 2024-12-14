from collections.abc import Sequence
from typing import Literal

from pydantic import JsonValue

from ome_zarr_models.v04.base import Base

__all__ = ["Axes", "Axis", "AxisType"]


AxisType = Literal["space", "time", "channel"]


class Axis(Base):
    """
    Model for an element of `Multiscale.axes`.

    See https://ngff.openmicroscopy.org/0.4/#axes-md.
    """

    name: str
    type: str | None = None
    unit: str | JsonValue | None = None


Axes = Sequence[Axis]
