from collections.abc import Sequence
from typing import Literal

from pydantic import JsonValue

from ome_zarr_models.base import BaseAttrs

__all__ = ["Axes", "Axis", "AxisType"]


AxisType = Literal["space", "time", "channel"]


Orientation = Literal[
    "left-to-right",
    "right-to-left",
    "anterior-to-posterior",
    "posterior-to-anterior",
    "inferior-to-superior",
    "superior-to-inferior",
    "dorsal-to-ventral",
    "ventral-to-dorsal",
    "dorsal-to-palmar",
    "palmar-to-dorsal",
    "dorsal-to-plantar",
    "plantar-to-dorsal",
    "rostral-to-caudal",
    "caudal-to-rostral",
    "cranial-to-caudal",
    "caudal-to-cranial",
    "proximal-to-distal",
    "distal-to-proximal",
]


class Axis(BaseAttrs):
    """
    Model for an element of `Multiscale.axes`.
    """

    # Explicitly name could be any JsonValue, but implicitly it must match Zarr array
    # dimension_names which limits it to str | None

    name: str | None
    type: str | None = None
    # Unit probably intended to be str, but the spec doesn't explicitly specify
    unit: str | JsonValue | None = None
    anatomicalOrientation: Orientation | None = None


Axes = Sequence[Axis]
