from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import Base
from ome_zarr_models.v04.plate import Plate

__all__ = ["HCSAttrs"]


class HCSAttrs(Base):
    """
    HCS metadtata attributes.
    """

    plate: Plate


class HCS(GroupSpec[HCSAttrs, ArraySpec | GroupSpec]):
    """
    An OME-zarr high-content screening (HCS) dataset representing a single plate.
    """
