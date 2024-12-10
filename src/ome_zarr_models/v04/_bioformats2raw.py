from typing import Literal

from pydantic import Field, JsonValue

from ome_zarr_models.base import Base
from ome_zarr_models.v04.plate import Plate


class BioFormats2RawAttrs(Base):
    """
    A model of the attributes contained in a bioformats2raw zarr group.
    """

    bioformats2raw_layout: Literal[3] = Field(..., alias="bioformats2raw.layout")
    plate: Plate | None = None
    series: JsonValue | None = None
