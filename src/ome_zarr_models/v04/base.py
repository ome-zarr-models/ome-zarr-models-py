from typing import Generic, Literal, TypeVar

from ome_zarr_models.base import BaseAttrs, BaseGroup

T = TypeVar("T", bound=BaseAttrs)


class BaseGroupv04(BaseGroup[T], Generic[T]):
    """
    Base class for all v0.4 OME-Zarr groups.
    """

    @property
    def ome_zarr_version(self) -> Literal["0.4"]:
        """
        OME-Zarr version.
        """
        return "0.4"
