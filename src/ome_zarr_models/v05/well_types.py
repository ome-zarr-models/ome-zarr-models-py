from typing import Literal

from pydantic import Field

import ome_zarr_models.common.well_types
from ome_zarr_models.common.well_types import WellImage

__all__ = ["WellImage", "WellMeta"]


class WellMeta(ome_zarr_models.common.well_types.WellMeta):
    """
    Metadata for a single well.
    """

    version: Literal["0.5"] | None = Field(
        default="0.5", description="Version of the well specification"
    )
