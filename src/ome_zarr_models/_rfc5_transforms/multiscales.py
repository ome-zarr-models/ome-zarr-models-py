from __future__ import annotations

from typing import Self

from pydantic import (
    Field,
    JsonValue,
    field_validator,
    model_validator,
    BaseModel,
)

from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformationType,
)
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import check_length

__all__ = ["Dataset"]


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    path: str
    coordinateTransformations: tuple[CoordinateTransformationType, ...] = Field(
        ..., min_length=1, max_length=1
    )

    @field_validator("coordinateTransformations", mode="before")
    def _ensure_scale_translation(
        transforms_obj: object,
    ) -> object:
        """
        Ensures that
        - a single transformation is present
        - the first transformation is a scale
        - if there are more than one transformation, they must be 2
        - and the second transformation is a translation
        """
        # the before validation is used to simplify the error messages

        class Transforms(BaseModel):
            transforms: tuple[CoordinateTransformationType, ...]

        transforms = Transforms(transforms=transforms_obj).transforms
        check_length(transforms, valid_lengths=[1], variable_name="transforms")

        transform = transforms[0]
        if transform.type == "sequence":
            check_length(
                transform.transformations,
                valid_lengths=[2],
                variable_name="transform.transforms",
            )
            first, second = transform.transformations
            if first.type != "scale":
                msg = (
                    "When the first (and only) element in `coordinateTransformations`"
                    " is a `Sequence`, the first element must be a `Scale` transform. "
                    f"Got {first} instead."
                )
                raise ValueError(msg)
            if second.type != "translation":
                msg = (
                    "When the first (and only) element in `coordinateTransformations`"
                    " is a `Sequence`, the second element must be a `Translation` "
                    f"transform. Got {second} instead."
                )
                raise ValueError(msg)
        elif transform.type != "scale":
            msg = (
                "The first transformation in `coordinateTransformations` "
                "must either be a `Scale` transform or a `Sequence` transform. "
                f"Got {transform} instead."
            )
            raise ValueError(msg)

        return transforms_obj

    @field_validator("coordinateTransformations", mode="after")
    @classmethod
    def _ensure_transform_dimensionality(
        cls,
        transforms: tuple[CoordinateTransformationType, ...],
    ) -> tuple[CoordinateTransformationType, ...]:
        """
        Ensures that the dimensionality of the transformation matches the
        dimensionality of the dataset.
        """
        maybe_sequence = transforms[0]
        if maybe_sequence.type == "sequence":
            first, second = maybe_sequence.transformations
            if len(first.scale) != len(second.translation):
                raise ValueError(
                    "The length of the scale and translation vectors must be the same."
                    f"Got {len(first.scale)} and {len(second.translation)}."
                )
        return transforms


class Multiscale(BaseAttrs):
    """
    An element of multiscales metadata.
    """

    coordinateSystems: tuple[CoordinateSystem, ...] = Field(..., min_length=1)
    datasets: tuple[Dataset, ...] = Field(..., min_length=1)
    coordinateTransformations: tuple[CoordinateTransformationType, ...] | None = None
    metadata: JsonValue = None
    name: JsonValue | None = None
    type: JsonValue = None

    @property
    def ndim(self) -> int:
        """
        Dimensionality of the data described by this metadata.

        Determined by the length of the axes attribute.
        """
        output_cs_name = self.datasets[0].coordinateTransformations[0].output
        output_cs: CoordinateSystem | None = None
        for cs in self.coordinateSystems:
            if cs.name == output_cs_name:
                output_cs = cs
                break
        assert output_cs is not None
        return len(output_cs.axes)

    @model_validator(mode="after")
    def _ensure_same_output_cs_for_all_datasets(data: Self) -> Self:
        """
        Ensure that all datasets have the same output coordinate system.
        """
        output_coordinate_systems = set()
        for dataset in data.datasets:
            output_coordinate_systems.add(dataset.coordinateTransformations[0].output)
        if len(output_coordinate_systems) > 1:
            raise ValueError(
                "All `Dataset` instances of a `Multiscale`  must have the same output "
                "coordinate system. Got {output_coordinate_systems}."
            )
        return data

    @field_validator("datasets", mode="after")
    @classmethod
    def _ensure_ordered_scales(cls, datasets: list[Dataset]) -> list[Dataset]:
        """
        Make sure datasets are ordered from highest resolution to smallest.
        """
        scale_transforms = []
        for dataset in datasets:
            (transform,) = dataset.coordinateTransformations
            if transform.type == "scale":
                scale_transforms.append(transform)
            else:
                assert transform.type == "sequence"
                scale = transform.transformations[0]
                scale_transforms.append(scale)

        scales = [s.scale for s in scale_transforms]
        for i in range(len(scales) - 1):
            s1, s2 = scales[i], scales[i + 1]
            is_ordered = all(s1[j] <= s2[j] for j in range(len(s1)))
            if not is_ordered:
                raise ValueError(
                    f"Dataset {i} has a lower resolution (scales = {s1}) "
                    f"than dataset {i+1} (scales = {s2})."
                )
        return datasets

    @model_validator(mode="after")
    def check_cs_input_output(self) -> Self:
        """Check input and output for each coordinate system.

        The input and output must either be a path relative to the current file in the
        zarr store or must be a name that is present in the list of coordinate systems.
        """
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
                    "Invalid input in coordinate transformation: "
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
