from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v04.well import WellAttrs

__all__ = ["Well", "WellAttrs"]


class OMEWellAttrs(BaseOMEAttrs):
    ome: WellAttrs


class Well(GroupSpec[OMEWellAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr well dataset.
    """
