"""
For reference, see the [image label section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#label-md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import zarr
from pydantic import Field

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.image_label_types import Label
from ome_zarr_models.v04.multiscales import Multiscale

if TYPE_CHECKING:
    import zarr

__all__ = [
    "ImageLabel",
    "ImageLabelAttrs",
]


class ImageLabelAttrs(BaseAttrs):
    """
    Attributes for an image label object.
    """

    image_label: Label = Field(..., alias="image-label")
    multiscales: list[Multiscale]


class ImageLabel(BaseGroupv04[ImageLabelAttrs]):
    """
    An image label dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:
        """
        Create an instance of an OME-Zarr image from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-NGFF image label metadata.
        """
        # Use Image.from_zarr() to validate multiscale metadata
        Image.from_zarr(group)
        return super().from_zarr(group)  # type: ignore[no-any-return]
