"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#well-md).
"""

from collections.abc import Generator
from typing import TYPE_CHECKING

from ome_zarr_models.common.well import WellAttrs
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.image import Image

if TYPE_CHECKING:
    from pydantic_zarr.v2 import AnyGroupSpec


__all__ = ["Well", "WellAttrs"]


class Well(BaseGroupv04[WellAttrs]):
    """
    An OME-Zarr well group.
    """

    def get_image(self, i: int) -> Image:
        """
        Get a single image from this well.
        """
        image = self.attributes.well.images[i]
        image_path = image.path
        image_path_parts = image_path.split("/")
        group: AnyGroupSpec = self
        for part in image_path_parts:
            if group.members is None:
                raise RuntimeError(f"{group.members=}")
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
