from __future__ import annotations

from typing import Self

import zarr.errors
from pydantic import Field, model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.labels import Labels
from ome_zarr_models.v04.multiscales import Multiscale
from ome_zarr_models.v04.omero import Omero

__all__ = ["Image", "ImageAttrs"]


def _check_arrays_compatible(data: Image) -> Image:
    """
    Check that all the arrays referenced by the `multiscales` metadata meet the
    following criteria:
        - they exist
        - they are not groups
        - they have dimensionality consistent with the number of axes defined in the
          metadata.
    """
    multimeta = data.attributes.multiscales
    flat_self = data.to_flat()

    for multiscale in multimeta:
        multiscale_ndim = len(multiscale.axes)
        for dataset in multiscale.datasets:
            try:
                maybe_arr: ArraySpec | GroupSpec = flat_self[
                    "/" + dataset.path.lstrip("/")
                ]
                if isinstance(maybe_arr, GroupSpec):
                    msg = f"The node at {dataset.path} is a group, not an array."
                    raise ValueError(msg)
                arr_ndim = len(maybe_arr.shape)

                if arr_ndim != multiscale_ndim:
                    msg = (
                        f"The multiscale metadata has {multiscale_ndim} axes "
                        "which does not match the dimensionality of the array "
                        f"found in this group at {dataset.path} ({arr_ndim}). "
                        "The number of axes must match the array dimensionality."
                    )

                    raise ValueError(msg)
            except KeyError as e:
                msg = (
                    f"The multiscale metadata references an array that does not "
                    f"exist in this group: {dataset.path}"
                )
                raise ValueError(msg) from e
    return data


class ImageAttrs(BaseAttrs):
    """
    Model for the metadata of OME-Zarr data.

    See https://ngff.openmicroscopy.org/0.4/#image-layout.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )
    omero: Omero | None = None


class Image(GroupSpec[ImageAttrs, ArraySpec | GroupSpec], BaseGroupv04):  # type: ignore[misc]
    """
    An OME-Zarr multiscale dataset.
    """

    _check_arrays_compatible = model_validator(mode="after")(_check_arrays_compatible)

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:
        """
        Create an instance of an OME-Zarr image from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-NGFF image metadata.
        """
        # on unlistable storage backends, the members of this group will be {}
        guess = GroupSpec.from_zarr(group, depth=0)

        multi_meta = ImageAttrs.model_validate(guess.attributes)
        members_tree_flat = {}
        for multiscale in multi_meta.multiscales:
            for dataset in multiscale.datasets:
                array_path = f"{group.path}/{dataset.path}"
                try:
                    array = zarr.open_array(
                        store=group.store, path=array_path, mode="r"
                    )
                    array_spec = ArraySpec.from_zarr(array)
                except zarr.errors.ArrayNotFoundError as e:
                    msg = (
                        f"Expected to find an array at {array_path}, "
                        "but no array was found there."
                    )
                    raise ValueError(msg) from e
                except zarr.errors.ContainsGroupError as e:
                    msg = (
                        f"Expected to find an array at {array_path}, "
                        "but a group was found there instead."
                    )
                    raise ValueError(msg) from e
                members_tree_flat["/" + dataset.path] = array_spec

        try:
            labels_group = zarr.open_group(store=group.store, path="labels", mode="r")
            members_tree_flat["/labels"] = GroupSpec.from_zarr(labels_group)
        except zarr.errors.GroupNotFoundError:
            pass

        members_normalized = GroupSpec.from_flat(members_tree_flat)

        guess_inferred_members = guess.model_copy(
            update={"members": members_normalized.members}
        )
        return cls(**guess_inferred_members.model_dump())

    @property
    def labels(self) -> Labels | None:
        """
        Any labels datasets contained in this image group.

        Returns None if no labels are present.
        """
        if "labels" not in self.members:
            return None

        labels_group = self.members["labels"]

        return Labels(attributes=labels_group.attributes, members=labels_group.members)
