from typing import Literal

from pydantic import BaseModel, Field

from ome_zarr_models.common.image_label_types import Color, Property, Source
from ome_zarr_models.common.omero import Omero
from ome_zarr_models.v05.multiscales import Multiscale
from ome_zarr_models.v05.plate import Plate


class ImageLabel(BaseModel):
    """
    Base class for image-label metadata.
    """

    # TODO: validate
    # "All the values under the label-value (of colors) key MUST be unique."
    colors: tuple[Color, ...] | None = Field(
        default=None, description="Colours for showing the labels."
    )
    properties: tuple[Property, ...] | None = Field(
        default=None, description="Additional properties for each label value."
    )
    source: Source | None = Field(
        default=None,
        description="Information about the source data used to create the labels.",
    )


class LabelsGroupAttributes(BaseModel):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class OMEAttributesv05(BaseModel):
    """Model of the OME-metadata in a v0.6 OME-Zarr dataset.

    This is all metadata that can be found in the ome attribute.
    Fields that are not present in the document are set to None.
    """

    version: Literal["0.5"]
    multiscales: list[Multiscale] | None = None
    bioformats2raw_layout: Literal[3] | None = Field(
        default=None, alias="bioformats2raw.layout"
    )
    omero: Omero | None = None
    plate: Plate | None = None
    image_label: ImageLabel | None = Field(alias="image-label", default=None)
    labels: LabelsGroupAttributes | None = None
