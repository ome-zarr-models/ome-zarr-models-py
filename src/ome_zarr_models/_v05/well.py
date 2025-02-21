from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models._v05.well_types import WellMeta

__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseOMEAttrs):
    """
    Attributes for a well.
    """

    well: WellMeta


class Well(GroupSpec[BaseZarrAttrs[WellAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr well dataset.
    """
