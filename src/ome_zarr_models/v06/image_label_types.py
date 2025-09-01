from typing import Literal

from ome_zarr_models.common.image_label_types import (
    RGBA,
    Color,
    LabelBase,
    Property,
    Source,
    Uint8,
)

__all__ = ["RGBA", "Color", "LabelBase", "Property", "Source", "Uint8"]


class Label(LabelBase):
    """
    Metadata for a single image-label.
    """

    version: Literal["0.6"] | None = None
