from pydantic import Field
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models._v05.multiscales import Multiscale

__all__ = ["Image", "ImageAttrs"]


class ImageAttrs(BaseOMEAttrs):
    """
    Model for the metadata of OME-Zarr data.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )


class Image(GroupSpec[BaseZarrAttrs[ImageAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr image dataset.
    """
