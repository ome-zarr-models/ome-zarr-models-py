from pydantic import Field

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
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


class Image(BaseGroupv05[ImageAttrs]):
    """
    An OME-Zarr image dataset.
    """
