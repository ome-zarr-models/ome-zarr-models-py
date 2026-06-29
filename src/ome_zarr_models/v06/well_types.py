from typing import Annotated, Literal

from pydantic import AfterValidator, Field

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import (
    unique_items_validator,
    validate_zarr_node_name,
)
from ome_zarr_models.common.well_types import WellMeta as CommonWellMeta

__all__ = ["WellImage", "WellMeta"]


class WellImage(BaseAttrs):
    """
    A single image within a well.

    The ``path`` constraint was relaxed from alphanumeric to alphanumeric +
    ``.-_`` in NGFF 0.6 (see https://github.com/ome/ngff-spec/pull/71).
    """

    path: Annotated[str, AfterValidator(validate_zarr_node_name)]
    acquisition: int | None = Field(
        None, description="A unique identifier within the context of the plate"
    )


class WellMeta(CommonWellMeta):
    """
    Metadata for a single well.
    """

    images: Annotated[list[WellImage], AfterValidator(unique_items_validator)] = Field(  # type: ignore[assignment]
        ..., description="Images within a well"
    )
    version: Literal["0.6.dev4"] | None = Field(
        None, description="Version of the well specification"
    )
