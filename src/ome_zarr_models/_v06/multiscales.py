from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Self

from pydantic import (
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

import ome_zarr_models._v06.coordinate_transforms as transforms
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    Axis,
    CoordinateSystem,
    Identity,
    Scale,
    Sequence,
    Translation,
)
from ome_zarr_models.base import BaseAttrs

if TYPE_CHECKING:
    from ome_zarr_models.v05.multiscales import Multiscale as Multiscalev05
    from ome_zarr_models.v05.multiscales import (  # type: ignore[attr-defined]
        ValidTransform as ValidTransformv05,
    )

__all__ = ["Dataset", "Multiscale"]


VALID_NDIM = (2, 3, 4, 5)


class Multiscale(BaseAttrs):
    """
    An element of multiscales metadata.
    """

    coordinateSystems: tuple[CoordinateSystem, ...] = Field(..., min_length=1)
    datasets: tuple[Dataset, ...] = Field(..., min_length=1)
    coordinateTransformations: tuple[AnyTransform, ...] | None = None
    metadata: JsonValue = None
    name: JsonValue | None = None
    type: JsonValue = None

    @property
    def ndim(self) -> int:
        """
        Dimensionality of the data described by this metadata.
        """
        return self.intrinsic_coordinate_system.ndim

    @property
    def default_coordinate_system(self) -> CoordinateSystem:
        """
        The default coordinate system for this multiscales.

        Any references to this multiscales in coordinate transformations will resolve
        to this coordinate system.

        Notes
        -----
        This is the first entry in the `coordinateSystems` attribute.
        """
        return self.coordinateSystems[0]

    @property
    def intrinsic_coordinate_system(self) -> CoordinateSystem:
        """
        Physical coordinate system.

        Should be used for viewing and processing unless a use case dictates otherwise.
        A representation of the image in its native physical coordinate system.

        Notes
        -----
        This is the last entry in the `coordinateSystems` attribute.
        """
        return self.coordinateSystems[-1]

    @classmethod
    def from_v05(
        cls,
        multiscale_v05: Multiscalev05,
        intrinsic_system_name: str,
        top_level_system: CoordinateSystem | None = None,
    ) -> Self:
        """
        Convert a OME-Zarr 0.5 multiscales to OME-Zarr 0.6.

        Parameters
        ----------
        multiscale_v05 :
            OME-Zarr 0.5 multiscales
        intrinsic_system_name :
            Name to give the intrinsic coordinate system in the new multiscales.
        top_level_system :
            The coordinate system that the top-level coordinate transform in the
            multiscales transforms into. If the top-level transform is present, must be
            given. Otherwise, will not be used.
        """
        new_ms = cls(
            datasets=tuple(
                Dataset(
                    path=ds.path,
                    coordinateTransformations=(
                        _v05_transform_to_v06(ds.coordinateTransformations).model_copy(
                            update={
                                "input": ds.path,
                                "output": intrinsic_system_name,
                            }
                        ),
                    ),
                )
                for ds in multiscale_v05.datasets
            ),
            coordinateSystems=(
                CoordinateSystem(
                    name=intrinsic_system_name,
                    axes=tuple(
                        Axis(name=ax.name, type=ax.type, unit=ax.unit)
                        for ax in multiscale_v05.axes
                    ),
                ),
            ),
            metadata=multiscale_v05.metadata,
            name=multiscale_v05.name,
            type=multiscale_v05.type,
        )
        if multiscale_v05.coordinateTransformations is not None:
            if top_level_system is None:
                raise ValueError(
                    "top_level_system must be provided because a top-level "
                    "coordinate transform is present in the input multiscales."
                )
            new_ms = new_ms.model_copy(
                update={
                    "coordinateTransformations": (
                        _v05_transform_to_v06(
                            multiscale_v05.coordinateTransformations
                        ).model_copy(
                            update={
                                "input": intrinsic_system_name,
                                "output": top_level_system.name,
                            }
                        ),
                    ),
                    "coordinateSystems": (*new_ms.coordinateSystems, top_level_system),
                }
            )
        return new_ms

    @model_validator(mode="after")
    def _ensure_same_output_cs_for_all_datasets(data: Self) -> Self:
        """
        Ensure that all datasets have the same output coordinate system.

        Also ensures that the dimensionality of each dataset match the one of the
        output coordinate system.
        """
        output_cs_names = {
            dataset.coordinateTransformations[0].output for dataset in data.datasets
        }
        if len(output_cs_names) > 1:
            raise ValueError(
                "All `Dataset` instances of a `Multiscale`  must have the same output "
                f"coordinate system. Got {output_cs_names}."
            )
        return data

    # TODO: re-implement without assuming type of transform
    '''
    @field_validator("datasets", mode="after")
    @classmethod
    def _ensure_same_dimensionality_for_all_datasets(
        cls, datasets: list[Dataset]
    ) -> list[Dataset]:
        """
        Ensure that all datasets have the same dimensionality
        """
        dims = []
        for dataset in datasets:
            transformation = dataset.coordinateTransformations[0]
            if isinstance(transformation, Scale):
                dim = transformation.ndim
            else:
                assert isinstance(transformation, Sequence) and isinstance(
                    transformation.transformations[0], Scale
                )
                dim = transformation.transformations[0].ndim
            dims.append(dim)
        if len(set(dims)) > 1:
            raise ValueError(
                "All `Dataset` instances of a `Multiscale` must have the same "
                f"dimensionality. Got {dims}."
            )
        return datasets
    '''

    @model_validator(mode="after")
    def _ensure_axes_top_transforms(data: Self) -> Self:
        """
        Ensure that the length of the axes matches the dimensionality of the transforms
        defined in the top-level coordinateTransformations, if present.
        """
        if data.coordinateTransformations is not None:
            for tx in data.coordinateTransformations:
                if hasattr(tx, "ndim") and data.ndim != tx.ndim:
                    msg = (
                        f"The length of axes does not match the dimensionality of "
                        f"the {tx.type} transform in coordinateTransformations. "
                        f"Got {data.ndim} axes, but the {tx.type} transform has "
                        f"dimensionality {tx.ndim}"
                    )
                    raise ValueError(msg)
        return data

    @model_validator(mode="after")
    def _ensure_axes_dataset_transforms(data: Self) -> Self:
        """
        Ensure that the length of the axes matches the dimensionality of the transforms
        """
        for ds_idx, ds in enumerate(data.datasets):
            for tx in ds.coordinateTransformations:
                if hasattr(tx, "ndim") and data.ndim != tx.ndim:
                    msg = (
                        f"The length of axes does not match the dimensionality of "
                        f"the {tx.type} transform in "
                        f"datasets[{ds_idx}].coordinateTransformations. "
                        f"Got {data.ndim} axes, but the {tx.type} transform has "
                        f"dimensionality {tx.ndim}"
                    )
                    raise ValueError(msg)
        return data

    # TODO: possibly re-implement if the constraint for ordered scales still exists
    '''
    @field_validator("datasets", mode="after")
    @classmethod
    def _ensure_ordered_scales(cls, datasets: list[Dataset]) -> list[Dataset]:
        """
        Make sure datasets are ordered from highest resolution to smallest.
        """
        scale_transforms: list[Scale] = []
        for dataset in datasets:
            (transform,) = dataset.coordinateTransformations
            if isinstance(transform, Scale):
                scale_transforms.append(transform)
            else:
                assert isinstance(transform, Sequence) and isinstance(
                    transform.transformations[0], Scale
                )
                scale = transform.transformations[0]
                scale_transforms.append(scale)

        scales = [s.scale_vector for s in scale_transforms]
        for i in range(len(scales) - 1):
            s1, s2 = scales[i], scales[i + 1]
            is_ordered = all(s1[j] <= s2[j] for j in range(len(s1)))
            if not is_ordered:
                raise ValueError(
                    f"Dataset {i} has a lower resolution (scales = {s1}) "
                    f"than dataset {i + 1} (scales = {s2})."
                )
        return datasets
    '''

    @model_validator(mode="after")
    def check_dataset_transform_output(self) -> Self:
        """
        Check the output of all transforms in 'datasets' are the same.
        """
        outputs = []
        for dataset in self.datasets:
            for transform in dataset.coordinateTransformations:
                outputs.append(transform.output)
        if len(set(outputs)) > 1:
            raise ValueError(
                "All coordinate transform outputs inside 'datasets'"
                f" must be identical. Got {outputs}"
            )
        return self

    @model_validator(mode="after")
    def check_cs_input_output(self) -> Self:
        """
        Check input and output for each coordinate system.

        The input and output must either be a path relative to the current file in the
        zarr store or must be a name that is present in the list of coordinate systems.
        """
        # TODO: this test is only for coordinate transformations that are not part of a
        #  dataset. A second test for datasets should be added.
        if self.coordinateTransformations is None:
            return self
        cs_names = {cs.name for cs in self.coordinateSystems}

        # check input
        for transformation in self.coordinateTransformations:
            # TODO: add support for the input coordinate system being equal to the path
            #  of the array data. See more:
            # https://imagesc.zulipchat.com/#narrow/channel/469152-ome-zarr-models-py/topic/validating.20paths
            if transformation.input not in cs_names:
                raise ValueError(
                    "Invalid input in coordinate transformation "
                    f"'{transformation.name}': "
                    f"{transformation.input}. Must be one of {cs_names}."
                )

        # check output
        for transformation in self.coordinateTransformations:
            if transformation.output not in cs_names:
                raise ValueError(
                    "Invalid output in coordinate transformation: "
                    f"{transformation.output}. Must be one of {cs_names}."
                )
        return self


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    # TODO: validate that path resolves to an actual zarr array
    # TODO: can we validate that the paths must be ordered from highest resolution to
    # smallest using scale metadata?
    path: str
    coordinateTransformations: tuple[Scale | Identity | Sequence]

    @classmethod
    def build(
        cls,
        *,
        path: str,
        scale: typing.Sequence[float],
        translation: typing.Sequence[float] | None,
        coord_sys_output_name: str,
    ) -> Self:
        """
        Construct a `Dataset`.

        Parameters
        ----------
        path :
            Path to Zarr array.
        scale :
            Scale factors for this Dataset. These should be set so the output voxel size
            matches the highest resolution dataset in the multiscales.
        translation :
            A translation to apply. This is applied *after* the scaling.
        coord_sys_output_name :
            The name of the output coordinate system after this dataset is
            scaled and translated.
        """
        transform: transforms.Scale | transforms.Sequence
        if translation is None:
            transform = transforms.Scale(
                scale=tuple(scale), input=path, output=coord_sys_output_name
            )
        else:
            transform = transforms.Sequence(
                input=path,
                output=coord_sys_output_name,
                transformations=(
                    transforms.Scale(scale=tuple(scale)),
                    transforms.Translation(translation=tuple(translation)),
                ),
            )
        return cls(
            path=path,
            coordinateTransformations=(transform,),
        )

    @field_validator("coordinateTransformations", mode="after")
    @classmethod
    def _ensure_transform_dimensionality(
        cls,
        transforms: tuple[AnyTransform, ...],
    ) -> tuple[AnyTransform, ...]:
        """
        Ensures that the dimensionality of the scale and translation (when both present)
        match
        """
        # this test will not be needed anymore when
        # https://github.com/ome-zarr-models/ome-zarr-models-py/issues/188 is addressed
        if len(transforms) == 2:
            scale, translation = transforms
        elif (
            len(transforms) == 1
            and isinstance(transforms[0], Sequence)
            and len(transforms[0].transformations) == 2
        ):
            scale, translation = transforms[0].transformations
        else:
            return transforms

        if (
            isinstance(scale, Scale)
            and isinstance(translation, Translation)
            and scale.ndim != translation.ndim
        ):
            raise ValueError(
                "The length of the scale and translation vectors must be the same. "
                f"Got {scale.ndim} and {translation.ndim}."
            )
        return transforms


def _v05_transform_to_v06(transform: ValidTransformv05) -> Scale | Sequence:
    from ome_zarr_models.common.coordinate_transformations import (
        VectorScale,
        VectorTranslation,
    )

    # Scale (always present)
    if isinstance(transform[0], VectorScale):
        scale = Scale(scale=tuple(transform[0].scale))
    else:
        scale = Scale(path=transform[0].path)

    if len(transform) == 1:
        return scale

    else:
        # Translate
        if isinstance(transform[1], VectorTranslation):
            translate = Translation(translation=tuple(transform[1].translation))
        else:
            translate = Translation(path=transform[1].translation)
        return Sequence(transformations=(scale, translate))
