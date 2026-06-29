from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

from pydantic import JsonValue

from ome_zarr_models.base import BaseAttrs

if TYPE_CHECKING:
    from ome_zarr_models.v04.axes import Axis as AxisV04
    from ome_zarr_models.v06.coordinate_transforms import Axis as AxisV06

__all__ = ["Axes", "Axis", "AxisType"]


AxisType = Literal["space", "time", "channel"]


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

    def _to_v04(self) -> "AxisV04":
        from ome_zarr_models.v04.axes import Axis as AxisV04

        return AxisV04(name=self.name, type=self.type, unit=self.unit)

    def _to_v06(self) -> "AxisV06":
        from ome_zarr_models.v06.coordinate_transforms import Axis as AxisV06

        return AxisV06(name=self.name, type=self.type, unit=self.unit)


Axes = Sequence[Axis]
