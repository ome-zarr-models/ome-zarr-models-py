from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.plate import Plate

__all__ = ["HCS", "HCSAttrs"]


class HCSAttrs(BaseOMEAttrs):
    """
    HCS metadtata attributes.
    """

    plate: Plate


class HCS(BaseGroupv05[HCSAttrs]):
    """
    An OME-Zarr high content screening (HCS) dataset.
    """
