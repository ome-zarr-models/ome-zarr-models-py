"""
For reference, see the [image label section of the OME-zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#label-md).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import zarr
from pydantic import model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.image import Image, _check_arrays_compatible
from ome_zarr_models.v04.image_label_types import (
    Label,
)
from ome_zarr_models.v04.multiscales import Multiscale

if TYPE_CHECKING:
    import zarr

# ImageLabel is imported into the top level namespace
__all__ = [
    "ImageLabel",
    "ImageLabelAttrs",
]


class ImageLabelAttrs(BaseAttrs):
    """
    Attributes for an image label object.
    """

    image_label: Label
    multiscales: list[Multiscale]


class ImageLabel(GroupSpec[ImageLabelAttrs, ArraySpec | GroupSpec]):  # type: ignore[misc]
    """
    An image label dataset.
    """

    _check_arrays_compatible = model_validator(mode="after")(_check_arrays_compatible)

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:
        """
        Create an instance of an OME-zarr image from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-NGFF image label metadata.
        """
        return Image.from_zarr(group)
