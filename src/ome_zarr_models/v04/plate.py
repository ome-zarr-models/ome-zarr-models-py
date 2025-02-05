"""
For reference, see the [plate section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#plate-md).
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
    "Plate",
    "Row",
    "WellInPlate",
]


class Plate(PlateBase):
    """
    A single plate.
    """

    version: str | None = Field(None, description="Version of the plate specification")
