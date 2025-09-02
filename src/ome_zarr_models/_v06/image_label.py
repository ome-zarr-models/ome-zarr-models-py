from typing import Self

# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401
import zarr
from pydantic import Field

from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.image import Image
from ome_zarr_models._v06.image_label_types import Label
from ome_zarr_models._v06.multiscales import Multiscale

__all__ = ["ImageLabel", "ImageLabelAttrs"]


class ImageLabelAttrs(BaseOMEAttrs):
    """
    Attributes for an image label object.
    """

    image_label: Label | None = Field(alias="image-label", default=None)
    multiscales: list[Multiscale]


class ImageLabel(
    BaseGroupv06[ImageLabelAttrs],
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
        image = Image.from_zarr(group)
        return cls(attributes=image.attributes.model_dump(), members=image.members)
