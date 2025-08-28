from collections.abc import Sequence
from typing import Literal

from pydantic import JsonValue

from ome_zarr_models.base import BaseAttrs

__all__ = ["Axes", "Axis", "AxisType"]


AxisType = Literal["space", "time", "channel"]


class Axis(BaseAttrs):
    """
    Model for an element of `Multiscale.axes`.
    """

    # Explicitly name could be any JsonValue, but implicitly it must match Zarr array
    # dimension_names which limits it to str | None

    name: str | None = None
    type: str | None = None
    unit: str | JsonValue | None = None


Axes = Sequence[Axis]
