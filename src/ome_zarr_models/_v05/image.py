from pydantic import Field
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.multiscales import Multiscale
from ome_zarr_models.base import BaseAttrs

__all__ = ["Image", "ImageAttrs"]


class ImageAttrs(BaseAttrs):
    """
    Model for the metadata of OME-Zarr data.

    See https://ngff.openmicroscopy.org/0.4/#image-layout.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )


class Image(GroupSpec[BaseOMEAttrs[ImageAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr image dataset.
    """
