from typing import Literal

from pydantic import Field

import ome_zarr_models.common.well_types
from ome_zarr_models.common.well_types import WellImage

__all__ = ["WellImage", "WellMeta"]


class WellMeta(ome_zarr_models.common.well_types.WellMeta):
    """
    Metadata for a single well.
    """

    version: Literal["0.6"] | None = Field(
        None, description="Version of the well specification"
    )
