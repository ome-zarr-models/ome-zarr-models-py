from __future__ import annotations

from typing import TYPE_CHECKING, Self

import zarr.errors
from pydantic import Field, JsonValue, model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.coordinate_transformations import _build_transforms
from ome_zarr_models.common.validation import check_array_path
from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.labels import Labels
from ome_zarr_models.v04.multiscales import Dataset, Multiscale
from ome_zarr_models.v04.omero import Omero

if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = ["Image", "ImageAttrs"]


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


class Image(BaseGroupv04[ImageAttrs]):
    """
    An OME-Zarr multiscale dataset.
    """

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
        group_spec = GroupSpec.from_zarr(group, depth=0)

        multi_meta = ImageAttrs.model_validate(group_spec.attributes)
        members_tree_flat = {}
        for multiscale in multi_meta.multiscales:
            for dataset in multiscale.datasets:
                array_path = f"{group.path}/{dataset.path}"
                array_spec = check_array_path(group, array_path)
                members_tree_flat["/" + dataset.path] = array_spec

        try:
            labels_group = zarr.open_group(store=group.store, path="labels", mode="r")
            members_tree_flat["/labels"] = GroupSpec.from_zarr(labels_group)
        except zarr.errors.GroupNotFoundError:
            pass

        members_normalized = GroupSpec.from_flat(members_tree_flat)

        group_spec = group_spec.model_copy(
            update={"members": members_normalized.members}
        )
        return cls(**group_spec.model_dump())

    @classmethod
    def new(
        cls,
        *,
        array_specs: Sequence[ArraySpec],
        paths: Sequence[str],
        axes: Sequence[Axis],
        scales: Sequence[Sequence[float]],
        translations: Sequence[Sequence[float] | None],
        name: str | None = None,
        multiscale_type: str | None = None,
        metadata: JsonValue | None = None,
        global_scale: Sequence[float] | None = None,
        global_translation: Sequence[float] | None = None,
    ) -> Image:
        """
        Create a new `Image` from a sequence of multiscale arrays
        and spatial metadata.

        Parameters
        ----------
        array_specs :
            A sequence of array specifications that collectively represent the same
            image at multiple levels of detail.
        paths :
            The paths to the arrays within the new Zarr group.
        axes :
            `Axis` objects describing the axes of the arrays.
        scales :
            For each array, a scale value for each axis of the array.
        translations :
            For each array, a translation value for each axis the array.
        name :
            A name for the multiscale collection.
        multiscale_type :
            Type of downscaling method used to generate the multiscale image pyramid.
            Optional.
        metadata :
            Arbitrary metadata to store in the multiscales group.
        global_scale :
            A global scale value for each axis of every array.
        global_translation :
            A global translation value for each axis of every array.

        Notes
        -----
        This class does not store or copy any array data. To save array data,
        first write this class to a Zarr store, and then write data to the Zarr
        arrays in that store.
        """
        if len(array_specs) != len(paths):
            raise ValueError(
                f"Length of arrays (got {len(array_specs)=}) must be the same as "
                f"length of paths (got {len(paths)=})"
            )
        members_flat = {
            "/" + key.lstrip("/"): arr
            for key, arr in zip(paths, array_specs, strict=True)
        }

        if global_scale is None and global_translation is None:
            global_transform = None
        elif global_scale is None:
            raise ValueError(
                "If global_translation is specified, "
                "global_scale must also be specified."
            )
        else:
            global_transform = _build_transforms(global_scale, global_translation)

        if len(scales) != len(paths):
            raise ValueError(
                f"Length of 'scales' ({len(scales)}) does not match "
                f"length of 'paths' {len(paths)}"
            )
        if len(translations) != len(paths):
            raise ValueError(
                f"Length of 'translations' ({len(translations)}) does not match "
                f"length of 'paths' ({len(paths)})"
            )
        multimeta = Multiscale(
            axes=tuple(axes),
            datasets=tuple(
                Dataset.build(path=path, scale=scale, translation=translation)
                for path, scale, translation in zip(
                    paths, scales, translations, strict=True
                )
            ),
            coordinateTransformations=global_transform,
            metadata=metadata,
            name=name,
            type=multiscale_type,
            version="0.4",
        )
        return Image(
            members=GroupSpec.from_flat(members_flat).members,
            attributes=ImageAttrs(multiscales=(multimeta,)),
        )

    @model_validator(mode="after")
    def _check_arrays_compatible(self) -> Self:
        """
        Check that all the arrays referenced by the `multiscales` metadata meet the
        following criteria:
            - they exist
            - they are not groups
            - they have dimensionality consistent with the number of axes defined in the
              metadata.
        """
        multimeta = self.attributes.multiscales
        flat_self = self.to_flat()

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
        return self

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

    @property
    def datasets(self) -> tuple[tuple[Dataset, ...], ...]:
        """
        Get datasets stored in this image.

        The first index is for the multiscales.
        The second index is for the dataset inside that multiscales.
        """
        return tuple(
            tuple(dataset for dataset in multiscale.datasets)
            for multiscale in self.attributes.multiscales
        )
