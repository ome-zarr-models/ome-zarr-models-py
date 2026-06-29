"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#well-md).
"""

from typing import Literal

from pydantic import Field

from ome_zarr_models.common.well_types import WellImage
from ome_zarr_models.common.well_types import WellMeta as CommonWellMeta

__all__ = ["WellImage", "WellMeta"]


class WellMeta(CommonWellMeta):
    """
    Metadata for a single well.
    """

    version: Literal["0.4"] | None = Field(
        None, description="Version of the well specification"
    )
