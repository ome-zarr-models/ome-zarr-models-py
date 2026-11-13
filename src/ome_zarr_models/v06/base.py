from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar, Union

import pydantic_zarr
import pydantic_zarr.v3
from pydantic import BaseModel, field_validator

import ome_zarr_models._pydantic_zarr_compat as pzc
from ome_zarr_models.base import BaseAttrsv3, BaseGroup
from ome_zarr_models.exceptions import ValidationWarning

if TYPE_CHECKING:
    import zarr


class BaseOMEAttrs(BaseAttrsv3):
    """
    Base class for OME-Zarr 0.6 attributes.
    """

    version: Literal["0.6"]

    @field_validator("version", mode="before")
    @classmethod
    def _parse_version(cls, version: str) -> Literal["0.6"]:
        if version == "0.6":
            return "0.6"
        elif version == "0.6.dev4":
            warnings.warn(
                "Version number is '0.6.dev4', converting to '0.6'",
                ValidationWarning,
                stacklevel=2,
            )
            return "0.6"
        raise ValueError(f"Invalid version: '{version}'. Must be '0.6' or '0.6.dev4'.")


T = TypeVar("T", bound=BaseOMEAttrs)


class BaseZarrAttrs(BaseModel, Generic[T]):
    """
    Base class for zarr attributes in an OME-Zarr group.
    """

    ome: T


class BaseGroupv06(
    BaseGroup,
    pydantic_zarr.v3.GroupSpec[
        BaseZarrAttrs[T],
        Union["pydantic_zarr.v3.GroupSpec", "pydantic_zarr.v3.ArraySpec"],  # type: ignore[type-arg, unused-ignore]
    ],
    Generic[T],
):
    """
    Base class for all v0.6 OME-Zarr groups.
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
        return pzc.read_group_v3(cls, group)

    @property
    def ome_zarr_version(self) -> Literal["0.6"]:
        """
        OME-Zarr version.
        """
        return "0.6"

    @property
    def ome_attributes(self) -> T:
        """
        OME attributes.
        """
        return self.attributes.ome
