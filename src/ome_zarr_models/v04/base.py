from typing import Generic, Literal, Self, TypeVar

import zarr
from pydantic_zarr.v2 import GroupSpec, TBaseItem

from ome_zarr_models.base import BaseAttrs, BaseGroup

T = TypeVar("T", bound=BaseAttrs)


class BaseGroupv04(BaseGroup, GroupSpec[T, TBaseItem], Generic[T]):
    """
    Base class for all v0.4 OME-Zarr groups.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        return super().from_zarr(group)

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
