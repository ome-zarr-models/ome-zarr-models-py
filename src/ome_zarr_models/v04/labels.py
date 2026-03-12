from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import Field

from pydantic_zarr.v2 import GroupSpec

from ome_zarr_models._utils import _from_zarr_v2
from ome_zarr_models.base import BaseAttrsv2
from ome_zarr_models.v04.base import BaseGroupv04

if TYPE_CHECKING:
    import zarr
    from ome_zarr_models.v04.image_label import ImageLabel

__all__ = ["Labels", "LabelsAttrs"]


class LabelsAttrs(BaseAttrsv2):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )

    def get_optional_group_paths(self) -> dict[str, type['ImageLabel']]:
        from ome_zarr_models.v04.image_label import ImageLabel
        return {label: ImageLabel for label in self.labels}


class Labels(BaseGroupv04[LabelsAttrs]):
    """
    An OME-Zarr labels dataset.

    Notes
    -----
    The OME-Zarr 0.4 specification does not specify what data structures should
    be present at the paths listed in the `.labels` attribute. ome-zarr-models
    will try and parse any Zarr groups found at these paths as [](ImageLabel)
    groups.
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
        return _from_zarr_v2(group, cls, LabelsAttrs)

    def label_groups(self) -> dict[str, "ImageLabel"]:
        """
        Mapping from path to ImageLabel group, for all labels groups.
        """
        return {path: self.get_image_labels_group(path) for path in self.label_paths}

    def get_image_labels_group(self, path: str) -> "ImageLabel":
        """
        Get an image labels group at a given path.
        """
        from ome_zarr_models.v04.image_label import ImageLabel

        if self.members is None:
            raise RuntimeError(f"{self.members=}")
        spec = self.members[path]
        if not isinstance(spec, GroupSpec):
            raise RuntimeError(f"Node at {path} is not a group")

        return ImageLabel(attributes=spec.attributes, members=spec.members)
