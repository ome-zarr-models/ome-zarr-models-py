"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#well-md).
"""

from typing import Annotated, Literal

from pydantic import AfterValidator, Field

import ome_zarr_models.common.well_types
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import AlphaNumericConstraint, unique_items_validator

__all__ = ["WellImage", "WellMeta"]


class WellImage(BaseAttrs):
    """
    A single image within a well.
    """

    path: Annotated[str, AlphaNumericConstraint]
    acquisition: int | None = Field(
        None, description="A unique identifier within the context of the plate"
    )


class WellMeta(ome_zarr_models.common.well_types.WellMeta):
    """
    Metadata for a single well.
    """

    images: Annotated[list[WellImage], AfterValidator(unique_items_validator)] = Field(
        ..., description="Images within a well"
    )
    version: Literal["0.4"] | None = Field(
        None, description="Version of the well specification"
    )
