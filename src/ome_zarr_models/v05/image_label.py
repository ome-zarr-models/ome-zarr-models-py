from typing import Self

import zarr
from pydantic import Field

from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v05.image import Image
from ome_zarr_models.v05.image_label_types import Label
from ome_zarr_models.v05.multiscales import Multiscale

__all__ = ["ImageLabel", "ImageLabelAttrs"]


class ImageLabelAttrs(BaseOMEAttrs):
    """
    Attributes for an image label object.
    """

    image_label: Label = Field(..., alias="image-label")
    multiscales: list[Multiscale]


class ImageLabel(
    BaseGroupv05[ImageLabelAttrs],
):
    """
    An OME-Zarr image label dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an instance of an OME-Zarr image from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image label metadata.
        """
        # Use Image.from_zarr() to validate multiscale metadata
        Image.from_zarr(group)
        return super().from_zarr(group)
