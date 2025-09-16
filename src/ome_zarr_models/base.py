from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import pydantic_zarr.v2
    import pydantic_zarr.v3


class BaseAttrs(BaseModel):
    """
    The base pydantic model for all metadata classes
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        # This allows fields with aliases to be populated by either
        # their alias or class attribute name
        #
        # We use this so we can handle e.g., the "bioformats2raw.version"
        # key - names in Python can't contain a "."
        populate_by_name=True,
        frozen=True,
    )


class BaseAttrsv2(BaseAttrs):
    """
    Base attribute model for Zarr v2 groups (ie OME-Zarr 0.4).
    """

    def get_array_paths(self) -> list[str]:
        """
        Get a list of all array paths expected and required to live in the Group
        with these attributes.
        """
        return []

    def get_optional_array_paths(self) -> list[str]:
        """
        Get a list of all array paths expected but not required to live in the Group
        with these attributes.
        """
        return []

    def get_group_paths(self) -> dict[str, type[pydantic_zarr.v2.AnyGroupSpec]]:
        """
        Get a list of all group paths expected and required to live in the Group
        with these attributes.

        Must return a dictionary mapping paths to their GroupSpec class.
        """
        return {}

    def get_optional_group_paths(
        self,
    ) -> dict[str, type[pydantic_zarr.v2.AnyGroupSpec]]:
        """
        Get a list of all group paths expected but not required to live in the Group
        with these attributes.

        Must return a dictionary mapping paths to their GroupSpec class.
        """
        return {}


class BaseAttrsv3(BaseAttrs):
    """
    Base attribute model for Zarr v3 groups (ie OME-Zarr 0.5+).
    """

    def get_array_paths(self) -> list[str]:
        """
        Get a list of all array paths expected and required to live in the Group
        with these attributes.
        """
        return []

    def get_optional_array_paths(self) -> list[str]:
        """
        Get a list of all array paths expected but not required to live in the Group
        with these attributes.
        """
        return []

    def get_group_paths(self) -> dict[str, type[pydantic_zarr.v3.AnyGroupSpec]]:
        """
        Get a list of all group paths expected and required to live in the Group
        with these attributes.

        Must return a dictionary mapping paths to their GroupSpec class.
        """
        return {}

    def get_optional_group_paths(
        self,
    ) -> dict[str, type[pydantic_zarr.v3.AnyGroupSpec]]:
        """
        Get a list of all group paths expected but not required to live in the Group
        with these attributes.

        Must return a dictionary mapping paths to their GroupSpec class.
        """
        return {}


class BaseGroup(ABC):
    """
    Base class for all OME-Zarr groups.
    """

    @property
    @abstractmethod
    def ome_zarr_version(self) -> Literal["0.4", "0.5", "0.6"]:
        """
        Version of the OME-Zarr specification that this group corresponds to.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def ome_attributes(self) -> BaseAttrs:
        """
        OME attributes.
        """
        raise NotImplementedError
