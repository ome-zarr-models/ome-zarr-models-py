from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v04.image_label import ImageLabelAttrs

__all__ = ["ImageLabel", "ImageLabelAttrs"]


class OMEImageLabelAttrs(BaseOMEAttrs):
    ome: ImageLabelAttrs


class ImageLabel(GroupSpec[OMEImageLabelAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr image label dataset.
    """
