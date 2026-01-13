from typing import Literal

from pydantic import Field

from ome_zarr_models.common.image_label_types import (
    RGBA,
    Color,
    LabelBase,
    Property,
    Source,
    Uint8,
)

__all__ = ["RGBA", "Color", "Property", "Source", "Uint8"]


class Label(LabelBase):
    """
    Metadata for a single image-label.
    """

    version: Literal["0.4"] | None = Field(
        default=None, description="Version of the image-label specification."
    )
