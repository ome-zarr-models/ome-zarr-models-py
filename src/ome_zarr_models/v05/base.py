from typing import Literal

from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs, BaseGroup


class BaseOMEAttrs(BaseAttrs):
    """
    Base class for all OME attributes.
    """

    version: Literal["0.5"] = "0.5"
    ome: BaseAttrs


class BaseGroupv05(GroupSpec[BaseOMEAttrs, ArraySpec | GroupSpec], BaseGroup):  # type: ignore[misc]
    """
    Base class for all v0.5 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.5"]:
        """
        OME-Zarr version.
        """
        return "0.5"

    @property
    def ome_attributes(self) -> BaseAttrs:
        """
        OME-Zarr attributes.
        """
        return self.attributes.ome  # type: ignore[no-any-return]
