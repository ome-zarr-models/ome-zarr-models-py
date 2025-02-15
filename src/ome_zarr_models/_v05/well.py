import ome_zarr_models.v04.well
from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs

__all__ = ["Well", "WellAttrs"]


class WellAttrs(ome_zarr_models.v04.well.WellAttrs, BaseOMEAttrs):
    """
    Attributes for a well.
    """


class Well(BaseGroupv05[WellAttrs]):
    """
    An OME-Zarr well dataset.
    """
