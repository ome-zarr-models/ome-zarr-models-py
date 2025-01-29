from typing import Generic, Literal, TypeVar

from ome_zarr_models.base import BaseAttrs, BaseGroup

T = TypeVar("T", bound=BaseAttrs)


class BaseOMEAttrs(BaseAttrs, Generic[T]):
    """
    Base class for all OME attributes.
    """

    version: Literal["0.5"] = "0.5"
    ome: T


class BaseGroupv05(BaseGroup):
    """
    Base class for all v0.5 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.5"]:
        """
        OME-Zarr version.
        """
        return "0.5"
