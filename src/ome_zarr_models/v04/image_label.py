"""
For reference, see the [image label section of the OME-zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#label-md).
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Annotated, Literal, Self

import zarr
from pydantic import AfterValidator, Field, model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._utils import duplicates
from ome_zarr_models.v04.base import Base
from ome_zarr_models.v04.image import Image, _check_arrays_compatible
from ome_zarr_models.v04.multiscales import Multiscale

if TYPE_CHECKING:
    import zarr

# ImageLabel is imported into the top level namespace
__all__ = ["RGBA", "Color", "ImageLabelAttrs", "Property", "Source", "Uint8"]

Uint8 = Annotated[int, Field(strict=True, ge=0, le=255)]
RGBA = tuple[Uint8, Uint8, Uint8, Uint8]


class Color(Base):
    """
    A label value and RGBA.
    """

    label_value: int = Field(..., alias="label-value")
    rgba: RGBA | None


class Source(Base):
    """
    Source data for the labels.
    """

    # TODO: add validation that this path resolves to a zarr image group
    image: str | None = Field(
        default="../../", description="Relative path to a Zarr group of a key image."
    )


class Property(Base):
    """
    A single property.
    """

    label_value: int = Field(..., alias="label-value")


def _parse_colors(colors: tuple[Color] | None) -> tuple[Color] | None:
    if colors is None:
        msg = (
            "The field `colors` is `None`. `colors` should be a list of "
            "label descriptors."
        )
        warnings.warn(msg, stacklevel=1)
    else:
        dupes = duplicates(x.label_value for x in colors)
        if len(dupes) > 0:
            msg = (
                f"Duplicated label-value: {tuple(dupes.keys())}."
                "label-values must be unique across elements of `colors`."
            )
            raise ValueError(msg)

    return colors


class Label(Base):
    """
    Metadata for a single image-label.
    """

    # TODO: validate
    # "All the values under the label-value (of colors) key MUST be unique."
    colors: Annotated[tuple[Color, ...] | None, AfterValidator(_parse_colors)] = None
    properties: tuple[Property, ...] | None = None
    source: Source | None = None
    version: Literal["0.4"] | None

    @model_validator(mode="after")
    def _parse_model(self) -> Label:
        return _parse_imagelabel(self)


def _parse_imagelabel(model: Label) -> Label:
    """
    check that label_values are consistent across properties and colors
    """
    if model.colors is not None and model.properties is not None:
        prop_label_value = [prop.label_value for prop in model.properties]
        color_label_value = [color.label_value for color in model.colors]

        prop_label_value_set = set(prop_label_value)
        color_label_value_set = set(color_label_value)
        if color_label_value_set != prop_label_value_set:
            msg = (
                "Inconsistent `label_value` attributes in `colors` and `properties`."
                f"The `properties` attributes have `label_values` {prop_label_value}, "
                f"The `colors` attributes have `label_values` {color_label_value}, "
            )
            raise ValueError(msg)
    return model


class ImageLabelAttrs(Base):
    """
    Attributes for an image label object.
    """

    image_label: Label
    multiscales: list[Multiscale]


class ImageLabel(GroupSpec[ImageLabelAttrs, ArraySpec | GroupSpec]):
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
