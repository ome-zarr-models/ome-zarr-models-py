from __future__ import annotations

from pydantic import Field
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v05.base import BaseGroupv05

__all__ = ["Labels", "LabelsAttrs"]


class LabelsAttrs(BaseAttrs):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class Labels(GroupSpec[LabelsAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr labels dataset.
    """
