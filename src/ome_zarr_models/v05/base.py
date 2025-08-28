from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar, Union

from pydantic import BaseModel
from pydantic_zarr.v3 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs, BaseGroup

if TYPE_CHECKING:
    import zarr


class BaseOMEAttrs(BaseAttrs):
    """
    Base class for attributes under an OME-Zarr group.
    """

    version: Literal["0.5"]


T = TypeVar("T", bound="BaseOMEAttrs")


class BaseZarrAttrs(BaseModel, Generic[T]):
    """
    Base class for zarr attributes in an OME-Zarr group.
    """

    ome: T


class BaseGroupv05(
    BaseGroup,
    GroupSpec[BaseZarrAttrs[T], Union["GroupSpec", "ArraySpec"]],  # type: ignore[type-arg]
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

        Notes
        -----
        Creating models from unlistable stores is currently unsupported for this
        OME-Zarr model class.
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
