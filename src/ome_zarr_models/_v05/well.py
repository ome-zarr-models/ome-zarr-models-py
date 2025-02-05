from pydantic_zarr.v2 import ArraySpec, GroupSpec

import ome_zarr_models.v04.well
from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs

__all__ = ["Well", "WellAttrs"]


class WellAttrs(ome_zarr_models.v04.well.WellAttrs, BaseOMEAttrs):
    """
    Attributes for a well.
    """


class Well(GroupSpec[BaseZarrAttrs[WellAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr well dataset.
    """
