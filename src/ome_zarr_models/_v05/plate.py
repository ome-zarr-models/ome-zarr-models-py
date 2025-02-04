"""
For reference, see the [plate section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.5/index.html#plate-md).
"""

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

    version: str = Field(description="Version of the plate specification")
