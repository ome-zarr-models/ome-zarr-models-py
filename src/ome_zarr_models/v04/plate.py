"""
For reference, see the [plate section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#plate-md).
"""

from ome_zarr_models.common.plate import Acquisition, Column, Plate, Row, WellInPlate

__all__ = [
    "Acquisition",
    "Column",
    "Plate",
    "Row",
    "WellInPlate",
]
