"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#well-md).
"""

from collections.abc import Generator
from typing import Self

import zarr
from pydantic_zarr.v2 import AnyGroupSpec

from ome_zarr_models._utils import _from_zarr_v2
from ome_zarr_models.base import BaseAttrsv2
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.well_types import WellMeta

__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseAttrsv2):
    """
    Attributes for a well group.
    """

    well: WellMeta

    def get_optional_group_paths(self) -> dict[str, type[AnyGroupSpec]]:
        return {im.path: Image for im in self.well.images}


class Well(BaseGroupv04[WellAttrs]):
    """
    An OME-Zarr well group.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr well model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr well metadata.
        """
        return _from_zarr_v2(group, cls, WellAttrs)

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
