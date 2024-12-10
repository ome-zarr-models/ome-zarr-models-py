from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.v04.plate import Plate


class HCS(GroupSpec[Plate, ArraySpec | GroupSpec]):
    """
    An OME-zarr high-content screening (HCS) dataset representing a single plate.
    """
