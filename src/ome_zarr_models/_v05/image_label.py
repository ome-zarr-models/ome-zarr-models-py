from pydantic import Field
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.image_label_types import Label
from ome_zarr_models._v05.multiscales import Multiscale
from ome_zarr_models.base import BaseAttrs

__all__ = ["ImageLabel", "ImageLabelAttrs"]


class ImageLabelAttrs(BaseAttrs):
    """
    Attributes for an image label object.
    """

    image_label: Label = Field(..., alias="image-label")
    multiscales: list[Multiscale]


class OMEImageLabelAttrs(BaseOMEAttrs):
    ome: ImageLabelAttrs


class ImageLabel(GroupSpec[OMEImageLabelAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr image label dataset.
    """
