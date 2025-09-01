# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401

from ome_zarr_models.v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models.v06.well_types import WellMeta

__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseOMEAttrs):
    """
    Attributes for a well.
    """

    well: WellMeta


class Well(BaseGroupv06[WellAttrs]):
    """
    An OME-Zarr well dataset.
    """
