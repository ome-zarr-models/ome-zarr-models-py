# Import needed for pydantic type resolution
from typing import Self

import zarr

from ome_zarr_models._utils import _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.image import Image
from ome_zarr_models._v06.well_types import WellMeta

__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseOMEAttrs):
    """
    Attributes for a well.
    """

    well: WellMeta

    def get_optional_group_paths(self) -> dict[str, type[Image]]:  # type: ignore[override]
        return {im.path: Image for im in self.well.images}


class Well(BaseGroupv06[WellAttrs]):
    """
    An OME-Zarr well dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr well model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr well metadata.
        """
        return _from_zarr_v3(group, cls, WellAttrs)
