from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, ConfigDict


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


class BaseGroup(ABC):
    """
    Base class for all OME-Zarr groups.
    """

    @property
    @abstractmethod
    def ome_zarr_version(self) -> Literal["0.4", "0.5"]:
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
