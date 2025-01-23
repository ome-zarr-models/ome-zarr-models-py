"""
For reference, see the [image label section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/index.html#label-md).
"""

from __future__ import annotations

import warnings
from typing import Annotated, Literal, Self, TypeVar

from pydantic import AfterValidator, Field, model_validator

from ome_zarr_models._utils import duplicates
from ome_zarr_models.base import BaseAttrs

__all__ = ["RGBA", "Color", "Label", "LabelBase", "Property", "Source", "Uint8"]

Uint8 = Annotated[int, Field(strict=True, ge=0, le=255)]
RGBA = tuple[Uint8, Uint8, Uint8, Uint8]


class Color(BaseAttrs):
    """
    A label value and RGBA.
    """

    label_value: int = Field(..., alias="label-value")
    rgba: RGBA | None


class Source(BaseAttrs):
    """
    Source data for the labels.
    """

    # TODO: add validation that this path resolves to a zarr image group
    image: str | None = Field(
        default="../../", description="Relative path to a Zarr group of a key image."
    )


class Property(BaseAttrs):
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


class LabelBase(BaseAttrs):
    """
    Base class for image-label metadata.
    """

    # TODO: validate
    # "All the values under the label-value (of colors) key MUST be unique."
    colors: Annotated[tuple[Color, ...] | None, AfterValidator(_parse_colors)] = None
    properties: tuple[Property, ...] | None = None
    source: Source | None = None
    version: str | None = None

    @model_validator(mode="after")
    def _parse_model(self) -> Self:
        return _parse_imagelabel(self)


class Label(LabelBase):
    """
    Metadata for a single image-label.
    """

    version: Literal["0.4"] | None = None


_T = TypeVar("_T", bound=LabelBase)


def _parse_imagelabel(model: _T) -> _T:
    """
    Check that label_values are consistent across properties and colors
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
