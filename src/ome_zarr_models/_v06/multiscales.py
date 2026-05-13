from __future__ import annotations

import typing
from typing import Annotated, Self

from pydantic import (
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

import ome_zarr_models._v06.coordinate_transforms as transforms
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
    CoordinateSystemIdentifier,
    Identity,
    Scale,
    Sequence,
    Translation,
)
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import unique_items_validator

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
    def intrinsic_coordinate_system(self) -> CoordinateSystem:
        """
        Physical coordinate system.

        Should be used for viewing and processing unless a use case dictates otherwise.
        A representation of the image in its native physical coordinate system.

        Notes
        -----
        This is the `coordinateSystems` instance which is used output
        of all multiscale transformations defined in `datasets`.
        """
        output = self.datasets[0].coordinateTransformations[0].output
        if output is None:
            raise ValueError(
                "Output coordinate system in "
                f"{self.datasets[0].coordinateTransformations[0]} not found. "
            )
        return next(cs for cs in self.coordinateSystems if cs.name == output.name)

    @model_validator(mode="after")
    def _ensure_same_output_cs_for_all_datasets(data: Self) -> Self:
        """
        Ensure that all datasets have the same output coordinate system.

        Also ensures that the dimensionality of each dataset match the one of the
        output coordinate system.
        """
        output_cs = [
            ds.coordinateTransformations[0].output
            for ds in data.datasets
            if ds.coordinateTransformations[0].output is not None
        ]
        output_cs_names = {cs.name for cs in output_cs}
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
        Check input and output for each coordinate transformation.
        This is for transformations under multiscales > coordinateTransformations,
        not the multiscale transformations under
        multiscales > datasets > coordinateTransformations

        The input and output must either of:
        - a name that is present in the list of coordinate systems.
        - a downpointing path relative to the current file in the zarr store.
        """
        if self.coordinateTransformations is None:
            return self
        cs_names = {cs.name for cs in self.coordinateSystems}

        # check: additional coordinate transformations must have `name` set
        # in both input AND output
        for transformation in self.coordinateTransformations:
            # first check that both exist
            if transformation.input is None:
                raise ValueError(
                    "Transformations in coordinateTransformations must have an input."
                )
            if transformation.output is None:
                raise ValueError(
                    "Transformations in coordinateTransformations must have an output."
                )

            if transformation.input.name is None:
                raise ValueError(
                    "Input for coordinate transformations must provide"
                    " a coordinate system name"
                )

            if transformation.output.name is None:
                raise ValueError(
                    "Output for coordinate transformations must provide"
                    " a coordinate system name"
                )

            # The input CS must be defined in the same multiscales
            # Check that it exists in the list of coordinate systems
            if transformation.input.name not in cs_names:
                raise ValueError(
                    "Invalid input in coordinate transformation "
                    f"'{transformation.name}': "
                    f"{transformation.input.name}. Must be one of {cs_names}."
                )

            # if output path is None, then the cs name must be
            # among the coordinate systems defined in the multiscale
            # If output path is not None, then the coordinate system is
            # defined elsewhere.
            if (
                not transformation.output.path
                and transformation.output.name not in cs_names
            ):
                raise ValueError(
                    "Invalid output in coordinate transformation "
                    f"'{transformation.name}': {transformation.output.name}"
                    f". Must be one of {cs_names} or the path field must be set."
                )

            # TODO: if output has path attribute, also check that
            # the path is a multiscales group that hasa coordinate system
            # with the specified name in transformation.output.name.
            if transformation.output.path is not None:
                if ".." in transformation.output.path:
                    raise ValueError(
                        "Output paths in coordinate transformations "
                        f"must be downpointing. Got '{transformation.output.path}'."
                    )

        return self

    @field_validator("coordinateSystems", mode="after")
    @classmethod
    def check_unique_system_names(
        cls, systems: tuple[CoordinateSystem, ...]
    ) -> tuple[CoordinateSystem, ...]:
        sys_names = [sys.name for sys in systems]
        try:
            unique_items_validator(sys_names)
        except ValueError as e:
            raise ValueError(f"Duplicate coordinate system names: {sys_names}") from e
        return systems


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    # TODO: validate that path resolves to an actual zarr array
    # TODO: can we validate that the paths must be ordered from highest resolution to
    # smallest using scale metadata?
    path: str
    coordinateTransformations: tuple[
        Annotated[Scale | Identity | Sequence, Field(discriminator="type")]
    ]

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
                scale=tuple(scale),
                input=CoordinateSystemIdentifier(path=path),
                output=CoordinateSystemIdentifier(name=coord_sys_output_name),
            )
        else:
            transform = transforms.Sequence(
                input=CoordinateSystemIdentifier(path=path),
                output=CoordinateSystemIdentifier(name=coord_sys_output_name),
                transformations=(
                    transforms.Scale(scale=tuple(scale)),
                    transforms.Translation(translation=tuple(translation)),
                ),
            )
        return cls(
            path=path,
            coordinateTransformations=(transform,),
        )

    @model_validator(mode="after")
    def check_cs_input(self) -> Self:
        """
        Check the input of all multiscale transformations
        """
        for transformation in self.coordinateTransformations:
            # check that path field of input exists
            if transformation.input is None:
                raise ValueError("Transformations in datasets must have an input.")

            if transformation.input.path is None:
                raise ValueError("Input for dataset transforms must have a path field.")

            # check that path field of input matches the dataset path
            if transformation.input.path != self.path:
                raise ValueError(
                    "Input for a dataset transform must be the dataset array path: "
                    f"'{self.path}'. Got '{transformation.input.path}' instead."
                )

        return self

    @model_validator(mode="after")
    def check_cs_output(self) -> Self:
        """
        Check the output of all multiscale transformations
        """
        for transformation in self.coordinateTransformations:
            # check that output is a name (and not a path)
            if transformation.output is None:
                raise ValueError("Transformations in datasets must have an output.")

            if transformation.output.name is None:
                raise ValueError("Output name for dataset transforms must be set.")
        return self

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
