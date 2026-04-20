from collections.abc import Sequence
from typing import Literal, Self

from pydantic import BaseModel, JsonValue, model_validator

from ome_zarr_models.base import BaseAttrs

__all__ = ["Axes", "Axis", "AxisType"]


AxisType = Literal["space", "time", "channel"]


class Orientation(BaseModel):
    """
    Model for an orientation object.
    """

    type: JsonValue
    value: JsonValue


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
