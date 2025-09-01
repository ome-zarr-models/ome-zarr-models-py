# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401

from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v05.well_types import WellMeta

__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseOMEAttrs):
    """
    Attributes for a well.
    """

    well: WellMeta


class Well(BaseGroupv05[WellAttrs]):
    """
    An OME-Zarr well dataset.
    """
