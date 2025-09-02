from collections.abc import Sequence
from typing import Literal, Self

from pydantic import model_validator

from ome_zarr_models.common.axes import Axis as BaseAxis
from ome_zarr_models.common.axes import AxisType

__all__ = ["Axes", "Axis", "AxisType"]


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


class Axis(BaseAxis):
    """
    Model for an element of `Multiscale.axes`.
    """

    orientation: Orientation | None = None

    @model_validator(mode="after")
    def _check_orientation_only_on_spatial(self) -> Self:
        if self.type != "space" and self.orientation is not None:
            raise ValueError(
                f"Orientation can only be set on a spatial axis "
                f"(got Axis type='{self.type}')"
            )
        return self


Axes = Sequence[Axis]
