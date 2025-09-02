from collections.abc import Sequence
from typing import Self

from pydantic import BaseModel, JsonValue, model_validator

from ome_zarr_models.common.axes import Axis as BaseAxis
from ome_zarr_models.common.axes import AxisType

__all__ = ["Axes", "Axis", "AxisType"]


class Orientation(BaseModel):
    """
    Model for an orientation object.
    """

    type: JsonValue
    value: JsonValue


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
