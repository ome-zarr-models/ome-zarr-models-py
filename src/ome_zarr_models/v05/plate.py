"""
For reference, see the [plate section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.5/index.html#plate-md).
"""

import warnings
from typing import Self

from pydantic import Field, model_validator

from ome_zarr_models.common.plate import (
    Acquisition,
    Column,
    PlateBase,
    Row,
    WellInPlate,
)
from ome_zarr_models.exceptions import ValidationWarning

__all__ = [
    "Acquisition",
    "Column",
    "Plate",
    "PlateBase",
    "Row",
    "WellInPlate",
]


class Plate(PlateBase):
    """
    A single plate.
    """

    version: str = Field(
        default="0.5", description="Version of the plate specification"
    )

    @model_validator(mode="after")
    def check_version_given(self) -> Self:
        if "version" not in self.model_fields_set:
            warnings.warn(
                "'version' field not specified in plate metadata, "
                "setting version='0.5'",
                ValidationWarning,
                stacklevel=2,
            )
        return self
