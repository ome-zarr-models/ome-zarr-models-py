from typing import Literal, Self

import pydantic_zarr
import zarr
from pydantic import Field, JsonValue

from ome_zarr_models._utils import check_group_path  # type: ignore[attr-defined]
from ome_zarr_models.base import BaseAttrsv2
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.plate import Plate


class BioFormats2RawAttrs(BaseAttrsv2):
    """
    A model of the attributes contained in a bioformats2raw zarr group.
    """

    bioformats2raw_layout: Literal[3] = Field(..., alias="bioformats2raw.layout")
    plate: Plate | None = None
    series: JsonValue | None = None


class BioFormats2Raw(BaseGroupv04[BioFormats2RawAttrs]):
    """
    An OME-Zarr labels dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr BioFormats2Raw model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr labels metadata.
        """
        # on unlistable storage backends, the members of this group will be {}
        group_spec_in: pydantic_zarr.v2.AnyGroupSpec
        group_spec_in = pydantic_zarr.v2.GroupSpec.from_zarr(group, depth=0)
        attributes = BioFormats2RawAttrs.model_validate(group_spec_in.attributes)

        members_tree_flat: dict[
            str, pydantic_zarr.v2.AnyGroupSpec | pydantic_zarr.v2.AnyArraySpec
        ] = {}

        # Possible image paths
        image_index = 0
        while True:
            image_path = str(image_index)
            try:
                check_group_path(group, str(image_path), expected_zarr_version=2)
            except FileNotFoundError:
                break

            group_flat = Image.from_zarr(group[image_path]).to_flat()  # type: ignore[arg-type]
            for path in group_flat:
                members_tree_flat["/" + image_path + path] = group_flat[path]
            image_index += 1

        members_normalized: pydantic_zarr.v2.AnyGroupSpec = (
            pydantic_zarr.v2.GroupSpec.from_flat(members_tree_flat)
        )
        return cls(members=members_normalized.members, attributes=attributes)

    @property
    def image_paths(self) -> list[str]:
        """
        All paths to OME-Zarr images in this group.
        """
        image_index = 0
        image_paths = []
        if self.members is None:
            raise RuntimeError("Did not find any members in this group")
        while True:
            if str(image_index) in self.members:
                image_paths.append(str(image_index))
                image_index += 1
            else:
                break

        return image_paths

    @property
    def images(self) -> dict[str, Image]:
        """
        All images in this group.

        Returns
        -------
        images
            Mapping from image path to Image object.
        """
        return {
            path: Image.model_validate(self.members[path].model_dump())  # type: ignore[index]
            for path in self.image_paths
        }
