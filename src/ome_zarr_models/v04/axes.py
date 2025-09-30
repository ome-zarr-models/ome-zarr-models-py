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

    # Name probably intended to be str, but the spec doesn't explicitly specify
    name: JsonValue
    type: str | None = None
    # Unit probably intended to be str, but the spec doesn't explicitly specify
    unit: str | JsonValue | None = None


Axes = Sequence[Axis]
