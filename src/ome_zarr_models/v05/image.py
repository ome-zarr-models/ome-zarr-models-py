from collections.abc import Sequence
from typing import Any, Self

# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401
import zarr
import zarr.errors
from pydantic import Field, JsonValue, model_validator
from pydantic_zarr.v3 import AnyArraySpec, AnyGroupSpec, GroupSpec

from ome_zarr_models.common.coordinate_transformations import _build_transforms
from ome_zarr_models.common.validation import check_array_path
from ome_zarr_models.v05.axes import Axis
from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models.v05.labels import Labels
from ome_zarr_models.v05.multiscales import Dataset, Multiscale

__all__ = ["Image", "ImageAttrs"]


class ImageAttrs(BaseOMEAttrs):
    """
    Metadata for OME-Zarr image groups.
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

    @classmethod
    def new(
        cls,
        *,
        array_specs: Sequence[AnyArraySpec],
        paths: Sequence[str],
        axes: Sequence[Axis],
        scales: Sequence[Sequence[float]],
        translations: Sequence[Sequence[float] | None],
        name: str | None = None,
        multiscale_type: str | None = None,
        metadata: JsonValue | None = None,
        global_scale: Sequence[float] | None = None,
        global_translation: Sequence[float] | None = None,
    ) -> "Image":
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
        )
        return Image(
            members=GroupSpec.from_flat(members_flat).members,
            attributes=BaseZarrAttrs(
                ome=ImageAttrs(
                    multiscales=[
                        multimeta,
                    ],
                    version="0.5",
                ),
            ),
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
        multimeta = self.ome_attributes.multiscales
        flat_self = self.to_flat()

        for multiscale in multimeta:
            multiscale_ndim = len(multiscale.axes)
            multiscale_dim_names = tuple(a.name for a in multiscale.axes)
            for dataset in multiscale.datasets:
                try:
                    maybe_arr: AnyArraySpec | AnyGroupSpec = flat_self[
                        "/" + dataset.path.lstrip("/")
                    ]
                except KeyError as e:
                    msg = (
                        f"The multiscale metadata references an array that does not "
                        f"exist in this group: {dataset.path}"
                    )
                    raise ValueError(msg) from e

                if isinstance(maybe_arr, GroupSpec):
                    msg = f"The node at {dataset.path} is a group, not an array."
                    raise ValueError(msg)

                arr_ndim = len(maybe_arr.shape)
                if arr_ndim != multiscale_ndim:
                    msg = (
                        f"The multiscale metadata has {multiscale_ndim} axes "
                        "which does not match the dimensionality of the array "
                        f"found in this group at path '{dataset.path}' ({arr_ndim}). "
                        "The number of axes must match the array dimensionality."
                    )

                    raise ValueError(msg)

                arr_dim_names = maybe_arr.dimension_names
                if arr_dim_names is None:
                    msg = (
                        f"The array in this group at  '{dataset.path}' has no "
                        "dimension_names metadata."
                    )
                    raise ValueError(msg)
                elif arr_dim_names != multiscale_dim_names:
                    msg = (
                        f"The multiscale metadata has {multiscale_dim_names} "
                        "axes names "
                        "which does not match the dimension names of the array "
                        f"found in this group at path '{dataset.path}' "
                        f"({arr_dim_names}). "
                    )

                    raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def _check_label_multiscales(self) -> Self:
        """
        Check that the number of multiscale levels in any labels are the same as
        the base image.
        """
        if (labels := self.labels) is None:
            return self

        multimeta = self.ome_attributes.multiscales
        if len(multimeta) != 1:
            # If there's more than one multiscales, we can't check the labels
            # levels because we don't know which multiscales to check against
            # TODO: add a warning
            return self

        multiscales = multimeta[0]
        n_levels = len(multiscales.datasets)
        for path in labels.label_paths:
            image_label = labels.get_image_labels_group(path)
            if len(image_label.ome_attributes.multiscales) != 1:
                # If there's more than one multiscales, we can't check the labels
                # levels because we don't know which multiscales to check against
                # TODO: add a warning
                continue
            else:
                n_label_levels = len(image_label.ome_attributes.multiscales[0].datasets)
                if n_levels != n_label_levels:
                    raise RuntimeError(
                        f"Number of image label multiscale levels ({n_label_levels}) "
                        f"doesn't match number of image multiscale levels ({n_levels})."
                    )

        return self

    @property
    def labels(self) -> Labels | None:
        """
        Any labels datasets contained in this image group.

        Returns None if no labels are present.
        """
        if self.members is None or "labels" not in self.members:
            return None

        labels_group = self.members["labels"]
        if not isinstance(labels_group, GroupSpec):
            raise ValueError("Node at path 'labels' is not a group")

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
            for multiscale in self.ome_attributes.multiscales
        )
