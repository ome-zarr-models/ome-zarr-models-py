from pydantic import Field

from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs


class Bioformats2rawAttrs(BaseOMEAttrs):
    """
    Attributes for an OME-Zarr bioformats2raw dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class Bioformats2raw(
    BaseGroupv05[Bioformats2rawAttrs],
):
    """
    An OME-Zarr labels dataset.
    """
