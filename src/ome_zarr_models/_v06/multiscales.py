from __future__ import annotations

import typing
import warnings
from collections import Counter
from typing import TYPE_CHECKING, Annotated, Literal, Self, overload

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
from ome_zarr_models.common.validation import check_length, unique_items_validator

if TYPE_CHECKING:
    from ome_zarr_models.v04.multiscales import Multiscale as Multiscalev04
    from ome_zarr_models.v05.multiscales import Multiscale as Multiscalev05

__all__ = ["Dataset", "Multiscale"]


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

    @overload
    def to_version(self, version: Literal["0.4"]) -> Multiscalev04:
        pass

    @overload
    def to_version(
        self,
        version: Literal["0.5"],
    ) -> Multiscalev05:
        pass

    def to_version(
        self, version: Literal["0.4", "0.5"]
    ) -> Multiscalev05 | Multiscalev04:
        """
        Convert this Multiscale metadata to the specified version.

        Currently supported conversions are
        - 0.6 -> 0.5
        - 0.6 -> 0.4

        Parameters
        ----------
        version
            The version to convert to. Must be one of "0.4" or "0.5".
        """
        if version == "0.5":
            return self._to_v05()
        elif version == "0.4":
            return self._to_v05()._to_v04()
        else:
            raise ValueError(f"Unsupported version: {version}")

    def _to_v05(self) -> Multiscalev05:
        from ome_zarr_models.common.coordinate_transformations import (
            ValidTransform,
        )
        from ome_zarr_models.v05.axes import Axis as Axisv05
        from ome_zarr_models.v05.coordinate_transformations import (
            VectorScale,
            VectorTranslation,
        )
        from ome_zarr_models.v05.multiscales import (
            Dataset as Datasetv05,
        )
        from ome_zarr_models.v05.multiscales import (
            Multiscale as Multiscalev05,
        )

        intrinsic_cs = self.intrinsic_coordinate_system
        axes = tuple(
            [
                Axisv05(name=axis.name, type=axis.type, unit=axis.unit)
                for axis in intrinsic_cs.axes
            ]
        )

        datasets = []
        for ds in self.datasets:
            scale_transform: VectorScale | None = None
            translation_transform: VectorTranslation | None = None

            for tf in ds.coordinateTransformations:
                if isinstance(tf, Scale):
                    scale_transform = VectorScale(type="scale", scale=list(tf.scale))
                elif isinstance(tf, Sequence):
                    for sub_tf in tf.transformations:
                        if isinstance(sub_tf, Scale):
                            scale_transform = VectorScale(
                                type="scale", scale=list(sub_tf.scale)
                            )
                        elif isinstance(sub_tf, Translation):
                            translation_transform = VectorTranslation(
                                type="translation", translation=list(sub_tf.translation)
                            )
                        else:
                            raise ValueError(
                                f"Unsupported transform type: {type(sub_tf)}"
                            )

            if scale_transform is None:
                raise ValueError("No scale transform found")

            coord_transforms: ValidTransform
            if translation_transform is not None:
                coord_transforms = (scale_transform, translation_transform)
            else:
                coord_transforms = (scale_transform,)

            datasets.append(
                Datasetv05(path=ds.path, coordinateTransformations=coord_transforms)
            )

        if self.coordinateTransformations is not None:
            warnings.warn(
                "Coordinate transformations defined in "
                "multiscales > coordinateTransformations "
                "can currently not be converted to v0.5, "
                "as they are not supported in this version.",
                stacklevel=2,
            )

        new_ms = Multiscalev05(
            name=self.name,
            type=self.type,
            metadata=self.metadata,
            axes=axes,
            datasets=tuple(datasets),
        )
        return new_ms

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
        for cs in self.coordinateSystems:
            if cs.name == output.name:
                return cs
        raise ValueError(f"No coordinate systems have the name '{output.name}'")

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

    @field_validator("datasets", mode="after")
    @classmethod
    def _ensure_ordered_scales(cls, datasets: list[Dataset]) -> list[Dataset]:
        """
        Make sure datasets are ordered from the highest resolution to smallest.
        """
        scale_transforms: list[Scale] = []
        for dataset in datasets:
            (transform,) = dataset.coordinateTransformations
            if isinstance(transform, Scale):
                scale_transforms.append(transform)
            elif isinstance(transform, Identity):
                # TODO: is there some way we can compare this to other scales or
                #  identities?
                pass
            else:
                if not isinstance(transform, Sequence):
                    raise ValueError(
                        "Transform inside a multiscales must be a scale or sequence"
                    )
                if not isinstance(transform.transformations[0], Scale):
                    raise ValueError(
                        "Sequence transformation inside a multiscales must start with "
                        "a scale transform"
                    )
                scale = transform.transformations[0]
                scale_transforms.append(scale)

        scales = [s.scale for s in scale_transforms]
        for i in range(len(scales) - 1):
            s1, s2 = scales[i], scales[i + 1]
            is_ordered = all(s1[j] <= s2[j] for j in range(len(s1)))
            if not is_ordered:
                raise ValueError(
                    f"Dataset {i} has a lower resolution (scales = {s1}) "
                    f"than dataset {i + 1} (scales = {s2})."
                )
        return datasets

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

    @model_validator(mode="after")
    def _validate_axis_length(self) -> Self:
        """
        Ensures that there are between 2 and 5 axes (inclusive).
        """
        for cs in self.coordinateSystems:
            check_length(cs.axes, valid_lengths=(2, 3, 4, 5), variable_name="axes")
        return self

    @model_validator(mode="after")
    def _ensure_axis_types(self) -> Self:
        """
        Ensures that the following conditions are true:

        - there are only 2 or 3 axes with type `space`
        - the axes with type `space` are last in the list of axes
        - there is only 1 axis with type `time`
        - there is only 1 axis with type `channel`
        - there is only 1 axis with a type that is not `space`, `time`, or `channel`
        """
        for cs in self.coordinateSystems:
            print(cs)
            check_length(
                [ax for ax in cs.axes if ax.type == "space"],
                valid_lengths=[2, 3],
                variable_name="space axes",
            )
            check_length(
                [ax for ax in cs.axes if ax.type == "time"],
                valid_lengths=[0, 1],
                variable_name="time axes",
            )
            check_length(
                [ax for ax in cs.axes if ax.type == "channel"],
                valid_lengths=[0, 1],
                variable_name="channel axes",
            )
            check_length(
                [ax for ax in cs.axes if ax.type not in ["space", "time", "channel"]],
                valid_lengths=[0, 1],
                variable_name="custom axes",
            )

            axis_types = [ax.type for ax in cs.axes]
            type_census = Counter(axis_types)
            num_spaces = type_census["space"]
            if not all(a == "space" for a in axis_types[-num_spaces:]):
                msg = (
                    f"All space axes must be at the end of the axes list. "
                    f"Got axes with order: {axis_types}."
                )
                raise ValueError(msg)

            num_times = type_census["time"]
            if num_times == 1 and axis_types[0] != "time":
                msg = "Time axis must be at the beginning of axis list."
                raise ValueError(msg)

        return self


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
