from pydantic import Field

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.image_label_types import Label
from ome_zarr_models._v05.multiscales import Multiscale

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
