from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models._v05.plate import Plate

__all__ = ["HCS", "HCSAttrs"]


class HCSAttrs(BaseOMEAttrs):
    """
    HCS metadtata attributes.
    """

    plate: Plate


class HCS(GroupSpec[BaseZarrAttrs[HCSAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr high content screening (HCS) dataset.
    """
