from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v04.image import ImageAttrs

__all__ = ["Image", "ImageAttrs"]


class Image(GroupSpec[BaseOMEAttrs[ImageAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr image dataset.
    """
