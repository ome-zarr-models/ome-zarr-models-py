from pydantic import Field

from ome_zarr_models.common.omero import Omero
from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v05.multiscales import Multiscale

__all__ = ["Image", "ImageAttrs"]


class ImageAttrs(BaseOMEAttrs):
    """
    Metadata for OME-Zarr image groups.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )
    omero: Omero | None = None


class Image(BaseGroupv05[ImageAttrs]):
    """
    An OME-Zarr image dataset.
    """
