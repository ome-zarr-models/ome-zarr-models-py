from __future__ import annotations

from typing import Self

import zarr
import zarr.errors
from pydantic import Field
from pydantic_zarr.v2 import AnyArraySpec, AnyGroupSpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.base import BaseGroupv04

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
            A Zarr group that has valid OME-Zarr label metadata.
        """
        from ome_zarr_models.v05.image import Image

        attrs_dict = group.attrs.asdict()
        label_attrs = LabelsAttrs.model_validate(group.attrs.asdict())

        # Extract Zarr Image paths from multiscale metadata
        members_tree_flat: dict[str, AnyGroupSpec | AnyArraySpec] = {}
        for label_path in label_attrs.labels:
            try:
                image_group = group[label_path]
            except zarr.errors.GroupNotFoundError as err:
                raise ValueError(
                    f"Label path '{label_path}' not found in zarr group"
                ) from err
            if not isinstance(image_group, zarr.Group):
                raise RuntimeError(f"Node at path '{label_path}' is not a group")
            try:
                image_model = Image.from_zarr(image_group).to_flat()
                for path in image_model:
                    members_tree_flat["/" + label_path + path] = image_model[path]

            except Exception as err:
                msg = (
                    f"Error validating the label path '{label_path}' "
                    "as a OME-Zarr multiscales group."
                )
                raise RuntimeError(msg) from err

        members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
        return cls(attributes=attrs_dict, members=members_normalized.members)
