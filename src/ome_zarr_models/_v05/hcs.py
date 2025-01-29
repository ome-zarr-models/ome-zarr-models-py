from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.plate import Plate
from ome_zarr_models.base import BaseAttrs

__all__ = ["HCS", "HCSAttrs"]


class HCSAttrs(BaseAttrs):
    """
    HCS metadtata attributes.
    """

    plate: Plate


class HCS(GroupSpec[BaseOMEAttrs[HCSAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr high content screening (HCS) dataset.
    """
