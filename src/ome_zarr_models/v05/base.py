from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar, Union

import pydantic_zarr
import pydantic_zarr.v3
from pydantic import BaseModel

from ome_zarr_models.base import BaseAttrsv3, BaseGroup

if TYPE_CHECKING:
    import zarr


class BaseOMEAttrs(BaseAttrsv3):
    """
    Base class for OME-Zarr 0.5 attributes.
    """

    version: Literal["0.5"]


T = TypeVar("T", bound=BaseOMEAttrs)


class BaseZarrAttrs(BaseModel, Generic[T]):
    """
    Base class for zarr attributes in an OME-Zarr group.
    """

    ome: T


class BaseGroupv05(
    BaseGroup,
    pydantic_zarr.v3.GroupSpec[
        BaseZarrAttrs[T],
        Union["pydantic_zarr.v3.GroupSpec", "pydantic_zarr.v3.ArraySpec"],  # type: ignore[type-arg]
    ],
    Generic[T],
):
    """
    Base class for all v0.5 OME-Zarr groups.
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
    def ome_zarr_version(self) -> Literal["0.5"]:
        """
        OME-Zarr version.
        """
        return "0.5"

    @property
    def ome_attributes(self) -> T:
        """
        OME attributes.
        """
        return self.attributes.ome
