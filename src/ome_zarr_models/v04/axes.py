from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

from pydantic import JsonValue

from ome_zarr_models.base import BaseAttrs

if TYPE_CHECKING:
    from ome_zarr_models.v05.axes import Axis as AxisV05

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

    def _to_v05(self) -> "AxisV05":
        from ome_zarr_models.v05.axes import Axis as AxisV05

        if isinstance(self.name, str) or self.name is None:
            return AxisV05(name=self.name, type=self.type, unit=self.unit)
        else:
            raise RuntimeError(
                "Can only convert Axes that have names that are strings or None"
            )


Axes = Sequence[Axis]
