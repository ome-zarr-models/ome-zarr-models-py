"""
For reference, see the [plate section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.5/index.html#plate-md).
"""

from typing import Literal

from pydantic import Field

from ome_zarr_models.common.plate import (
    Acquisition,
    Column,
    PlateBase,
    Row,
    WellInPlate,
)

__all__ = [
    "Acquisition",
    "Column",
    "PlateBase",
    "Row",
    "WellInPlate",
]


class Plate(PlateBase):
    """
    A single plate.
    """

    version: Literal["0.5"] = Field(
        default="0.5", description="Version of the plate specification"
    )
