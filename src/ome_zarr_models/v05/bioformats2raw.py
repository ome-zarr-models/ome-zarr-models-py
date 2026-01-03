from typing import Literal, Self

import pydantic_zarr.v3
import zarr
from pydantic import Field, JsonValue

from ome_zarr_models._utils import check_group_path  # type: ignore[attr-defined]
from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v05.image import Image
from ome_zarr_models.v05.plate import Plate


class BioFormats2RawAttrs(BaseOMEAttrs):
    """
    A model of the attributes contained in a bioformats2raw zarr group.

    Warnings
    --------
    It is not recommended to write new bioformats2raw groups.
    bioformats2raw is designed to support existing legacy data, and will be superseded
    by other OME-Zarr features in the future.
    """

    bioformats2raw_layout: Literal[3] = Field(..., alias="bioformats2raw.layout")
    plate: Plate | None = None
    series: JsonValue | None = None


class BioFormats2Raw(
    BaseGroupv05[BioFormats2RawAttrs],
):
    """
    An OME-Zarr bioformats2raw dataset.

    Warnings
    --------
    It is not recommended to write new bioformats2raw groups.
    bioformats2raw is designed to support existing legacy data, and will be superseded
    by other OME-Zarr features in the future.

    Notes
    -----
    Currently this class does not offer a way to access OME-XML metadata.
    Please comment on [issue #374](https://github.com/ome-zarr-models/ome-zarr-models-py/issues/374)
    if you would find accessing OME-XML metadata useful.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr BioFormats2Raw model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr bioformats2raw metadata.
        """
        # on unlistable storage backends, the members of this group will be {}
        group_spec_in: pydantic_zarr.v3.AnyGroupSpec
        group_spec_in = pydantic_zarr.v3.GroupSpec.from_zarr(group, depth=0)

        members_tree_flat: dict[
            str, pydantic_zarr.v3.AnyGroupSpec | pydantic_zarr.v3.AnyArraySpec
        ] = {}

        # Possible image paths
        image_index = 0
        while True:
            image_path = str(image_index)
            try:
                check_group_path(group, str(image_path), expected_zarr_version=3)
            except FileNotFoundError:
                break

            group_flat = Image.from_zarr(group[image_path]).to_flat()  # type: ignore[arg-type]
            for path in group_flat:
                members_tree_flat["/" + image_path + path] = group_flat[path]
            image_index += 1

        members_normalized: pydantic_zarr.v3.AnyGroupSpec = (
            pydantic_zarr.v3.GroupSpec.from_flat(members_tree_flat)
        )
        return cls(
            members=members_normalized.members, attributes=group_spec_in.attributes
        )

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
