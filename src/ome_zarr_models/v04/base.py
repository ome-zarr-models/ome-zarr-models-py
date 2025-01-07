from typing import Literal

from ome_zarr_models.base import BaseGroup


class BaseGroupv04(BaseGroup):
    """
    Base class for all v0.4 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.4"]:
        """
        OME-Zarr version.
        """
        return "0.4"
