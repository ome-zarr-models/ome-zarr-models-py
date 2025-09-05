"""
For reference, see the [well section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#well-md).
"""

from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Self, TypeVar

import zarr
from pydantic_zarr.v2 import AnyGroupSpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import check_array_path
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.well_types import WellMeta

if TYPE_CHECKING:
    from pydantic_zarr.v2 import AnyArraySpec


__all__ = ["Well", "WellAttrs"]


class WellAttrs(BaseAttrs):
    """
    Attributes for a well group.
    """

    well: WellMeta

    def get_array_paths(self) -> list[str]:
        """
        Get a list of all array paths expected to live in this Well group
        with these attributes.
        """
        return [im.path for im in self.well.images]


TCls = TypeVar("TCls", bound=BaseGroupv04[Any])
TAttrs = TypeVar("TAttrs", bound=BaseAttrs)


def _from_zarr(
    group: zarr.Group,
    group_cls: type[TCls],
    attrs_cls: type[TAttrs],
    *,
    allow_missing_nodes: bool = False,
) -> TCls:
    """
    Create a GroupSpec from a potentially unlistable Zarr group.

    Parameters
    ----------
    group :
        Zarr group to create GroupSpec from.
    group_cls :
        Class of the Group to return.
    attrs_cls :
        Attributes class.
    allow_missing_nodes :
        If True, allow arrays or groups specified by the paths to be missing.
    """
    # on unlistable storage backends, the members of this group will be {}
    group_spec: AnyGroupSpec = GroupSpec.from_zarr(group, depth=0)
    attributes = attrs_cls.model_validate(group_spec.attributes)

    members_tree_flat: dict[str, AnyGroupSpec | AnyArraySpec] = {}
    expected_array_paths = attrs_cls.get_array_paths(attributes)

    for array_path in expected_array_paths:
        try:
            array_spec = check_array_path(group, array_path, expected_zarr_version=2)
        except ValueError as err:
            if not allow_missing_nodes:
                raise err
        else:
            members_tree_flat["/" + array_path] = array_spec

    members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
    return group_cls(members=members_normalized.members, attributes=attributes)


class Well(BaseGroupv04[WellAttrs]):
    """
    An OME-Zarr well group.
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
        return _from_zarr(group, cls, WellAttrs, allow_missing_nodes=True)

    def get_image(self, i: int) -> Image:
        """
        Get a single image from this well.
        """
        image = self.attributes.well.images[i]
        image_path = image.path
        image_path_parts = image_path.split("/")
        group: AnyGroupSpec = self
        for part in image_path_parts:
            if group.members is None:
                raise RuntimeError(f"{group.members=}")
            group = group.members[part]

        return Image(attributes=group.attributes, members=group.members)

    @property
    def n_images(self) -> int:
        """
        Number of images.
        """
        return len(self.attributes.well.images)

    @property
    def images(self) -> Generator[Image, None, None]:
        """
        Generator for all images in this well.
        """
        for i in range(self.n_images):
            yield self.get_image(i)
