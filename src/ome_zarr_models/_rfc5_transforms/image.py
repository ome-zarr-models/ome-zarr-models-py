from ome_zarr_models._rfc5_transforms.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._rfc5_transforms.multiscales import Multiscale
from ome_zarr_models._rfc5_transforms.labels import Labels
from typing import Any, Self

import pydantic_zarr  # noqa: F401
import zarr
import zarr.errors
from pydantic import Field
from pydantic_zarr.v3 import AnyArraySpec, AnyGroupSpec, GroupSpec

from ome_zarr_models.common.validation import check_array_path

__all__ = ["Image", "ImageAttrs"]


class ImageAttrs(BaseOMEAttrs):
    """
    Model for the metadata of OME-Zarr data.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )


class Image(BaseGroupv05[ImageAttrs]):
    """
    An OME-Zarr image dataset.
    """
    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr image model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        # on unlistable storage backends, the members of this group will be {}
        group_spec: GroupSpec[dict[str, Any], Any] = GroupSpec.from_zarr(group, depth=0)

        if "ome" not in group_spec.attributes:
            raise RuntimeError(f"Did not find 'ome' key in {group} attributes")
        multi_meta = ImageAttrs.model_validate(group_spec.attributes["ome"])
        members_tree_flat: dict[str, AnyGroupSpec | AnyArraySpec] = {}
        for multiscale in multi_meta.multiscales:
            for dataset in multiscale.datasets:
                array_path = f"{group.path}/{dataset.path}"
                array_spec = check_array_path(
                    group, array_path, expected_zarr_version=3
                )
                members_tree_flat["/" + dataset.path] = array_spec

        try:
            labels_group = zarr.open_group(store=group.store_path / "labels", mode="r")
            labels = Labels.from_zarr(labels_group)
            # members_tree_flat["/labels"] = labels
            labels_flat = labels.to_flat()
            for path in labels_flat:
                members_tree_flat[f"/labels{path}"] = labels_flat[path]

        except zarr.errors.GroupNotFoundError:
            pass

        members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
        return cls(attributes=group_spec.attributes, members=members_normalized.members)