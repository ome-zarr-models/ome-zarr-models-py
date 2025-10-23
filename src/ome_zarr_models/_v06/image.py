from collections.abc import Sequence
from typing import Self

# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401
import zarr
import zarr.errors
from pydantic import Field, JsonValue, model_validator
from pydantic_zarr.v3 import AnyArraySpec, AnyGroupSpec, GroupSpec

from ome_zarr_models._utils import TransformGraph, _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    Transform,
)
from ome_zarr_models._v06.labels import Labels
from ome_zarr_models._v06.multiscales import Dataset, Multiscale

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

    def get_array_paths(self) -> list[str]:
        paths = []
        for multiscale in self.multiscales:
            for dataset in multiscale.datasets:
                paths.append(dataset.path)
        return paths

    def get_optional_group_paths(self) -> dict[str, type[Labels]]:  # type: ignore[override]
        return {"labels": Labels}


class Image(BaseGroupv06[ImageAttrs]):
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
        return _from_zarr_v3(group, cls, ImageAttrs)

    @classmethod
    def new(
        cls,
        *,
        array_specs: Sequence[AnyArraySpec],
        paths: Sequence[str],
        scales: Sequence[Sequence[float]],
        translations: Sequence[Sequence[float] | None],
        name: str,
        multiscale_type: str | None = None,
        metadata: JsonValue | None = None,
        output_coord_transform: Transform,
        output_coord_system: CoordinateSystem,
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
        output_coord_transform :
            A coordinate transform that maps from the full resolution array
            (defined by zero translation, and unity scale factor) into the output
            coordinate system.
        output_coord_system :
            The output coordinate system after the array scales and translations, and
            the global scales and translations have been applied.

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
        array_coordinate_system = CoordinateSystem(
            name=f"{name}_array_coords",
            axes=tuple(
                Axis(name=axis.name, type="array", discrete=True)
                for axis in output_coord_system.axes
            ),
        )
        output_coord_transform = output_coord_transform.model_copy(
            update={
                "input": array_coordinate_system.name,
                "output": output_coord_system.name,
            }
        )
        multimeta = Multiscale(
            datasets=tuple(
                Dataset.build(
                    path=path,
                    scale=scale,
                    translation=translation,
                    coord_sys_output_name=f"{name}_array_coords",
                )
                for path, scale, translation in zip(
                    paths, scales, translations, strict=True
                )
            ),
            coordinateTransformations=(output_coord_transform,),
            coordinateSystems=(
                array_coordinate_system,
                output_coord_system,
            ),
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
                    version="0.6",
                )
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
            multiscale_ndim = multiscale.ndim
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

    def transform_graph(self) -> TransformGraph:
        """
        Create a coordinate transformation graph for this image.
        """
        graph = TransformGraph()

        for multiscales in self.ome_attributes.multiscales:
            # Coordinate transforms
            if multiscales.coordinateTransformations is not None:
                for transform in multiscales.coordinateTransformations:
                    graph.add_transform(transform)
            # Coordinate transforms in datasets
            for dataset in multiscales.datasets:
                for transform in dataset.coordinateTransformations:
                    graph.add_transform(transform)

        return graph
