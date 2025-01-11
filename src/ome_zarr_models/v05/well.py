"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.5/#well-md).
"""

from collections.abc import Generator

from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v05.base import BaseGroupv05
from ome_zarr_models.v05.image import Image
from ome_zarr_models.v05.well_types import WellMeta

# WellGroup is defined one level higher
__all__ = ["WellAttrs"]


class WellAttrs(BaseAttrs):
    """
    Attributes for a well group.
    """

    well: WellMeta


class Well(GroupSpec[WellAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    def get_image(self, i: int) -> Image:
        """
        Get a single image from this well.
        """
        image = self.attributes.well.images[i]
        image_path = image.path
        image_path_parts = image_path.split("/")
        group = self
        for part in image_path_parts:
            group = group.members[part]

        return Image(attributes=group.attributes, members=group.members)

    @property
    def n_images(self) -> int:
        """
        Number of images.
        """
        return len(self.attributes.well.images)

    @property
    def images(self) -> Generator[Image, None, None]:
        """
        Generator for all images in this well.
        """
        for i in range(self.n_images):
            yield self.get_image(i)
