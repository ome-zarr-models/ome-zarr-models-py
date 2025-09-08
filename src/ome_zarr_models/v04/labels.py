from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import Field
from pydantic_zarr.v2 import AnyGroupSpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.base import BaseGroupv04

if TYPE_CHECKING:
    import zarr

__all__ = ["Labels", "LabelsAttrs"]


class LabelsAttrs(BaseAttrs):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class Labels(BaseGroupv04[LabelsAttrs]):
    """
    An OME-Zarr labels dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr labels model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr labels metadata.
        """
        gs: AnyGroupSpec = GroupSpec.from_zarr(group, depth=0)
        return cls(attributes=gs.attributes, members=gs.members)
