from typing import Generic, Literal, Self, TypeVar

import zarr
from pydantic_zarr.v2 import GroupSpec, TBaseItem

import ome_zarr_models._pydantic_zarr_compat as pzc
from ome_zarr_models.base import BaseAttrsv2, BaseGroup

T = TypeVar("T", bound=BaseAttrsv2)


class BaseGroupv04(BaseGroup, GroupSpec[T, TBaseItem], Generic[T]):
    """
    Base class for all v0.4 OME-Zarr groups.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override, unused-ignore]
        """
        Create an OME-Zarr model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        return pzc.read_group_v2(cls, group)

    @property
    def ome_zarr_version(self) -> Literal["0.4"]:
        """
        OME-Zarr version.
        """
        return "0.4"

    @property
    def ome_attributes(self) -> T:
        """
        OME attributes.
        """
        return self.attributes
