from __future__ import annotations

from typing import Self

from pydantic import (
    BaseModel,
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
    VectorScale,
    VectorTranslation,
)
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import check_length

__all__ = ["Dataset", "Multiscale"]


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    path: str
    # TODO: suggest John not to have a tuple for the coordinate transformations of a
    #  dataset, since it's either a single scale or a single sequence (with a scale
    #  and a translation)
    coordinateTransformations: list[CoordinateTransformation] = Field(
        ..., min_length=1, max_length=1
    )

    # the before validation is used to simplify the error messages
    @field_validator("coordinateTransformations", mode="before")
    def _ensure_scale_translation(
        transforms_obj: object,
    ) -> object:
        """
        Ensures that
        - a single transformation is present
        - such transformation is a scale
        - if such transformation is a sequence, ensure that its length is 2 and that
          the first transformation is a scale and the second a translation
        """
        # the class below simplifies error messages since we are in a before validator;
        # see more: ome_zarr_models.common.multiscales.Dataset

        class Transforms(BaseModel):
            transforms: list[CoordinateTransformation]

        transforms = Transforms(transforms=transforms_obj).transforms
        check_length(transforms, valid_lengths=[1], variable_name="transforms")

        transform = transforms[0]
        if transform.type == "sequence":
            check_length(
                transform.transformations,
                valid_lengths=[2],
                variable_name="transform.transforms (i.e. transformations composing "
                "the sequence)",
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
        transforms: tuple[CoordinateTransformation, ...],
    ) -> tuple[CoordinateTransformation, ...]:
        """
        Ensures that the dimensionality of the scale and translation (when both present)
        match
        """
        # this test will not be needed anymore when
        # https://github.com/ome-zarr-models/ome-zarr-models-py/issues/188 is addressed
        maybe_sequence = transforms[0]
        if maybe_sequence.type == "sequence":
            first, second = maybe_sequence.transformations
            if (
                isinstance(first, VectorScale)
                and isinstance(second, VectorTranslation)
                and len(first.scale) != len(second.translation)
            ):
                raise ValueError(
                    "The length of the scale and translation vectors must be the same. "
                    f"Got {len(first.scale)} and {len(second.translation)}."
                )
        return transforms


class Multiscale(BaseAttrs):
    """
    An element of multiscales metadata.
    """

    coordinateSystems: tuple[CoordinateSystem, ...] = Field(..., min_length=1)
    datasets: tuple[Dataset, ...] = Field(..., min_length=1)
    coordinateTransformations: tuple[CoordinateTransformation, ...] | None = None
    metadata: JsonValue = None
    name: JsonValue | None = None
    type: JsonValue = None

    def get_coordinate_system(self, name: str) -> CoordinateSystem:
        """
        Get a coordinate system by name.
        """
        for cs in self.coordinateSystems:
            if cs.name == name:
                return cs
        raise ValueError(f"No coordinate system with name {name} found.")

    @property
    def ndim(self) -> int:
        """
        Dimensionality of the data described by this metadata.
        """
        output_cs_name = self.datasets[0].coordinateTransformations[0].output
        assert output_cs_name is not None
        output_cs = self.get_coordinate_system(name=output_cs_name)
        return len(output_cs.axes)

    @property
    def default_coordinate_system(self) -> CoordinateSystem:
        """
        Property returning the default coordinate system (i.e. the first entry).

        The default coordinate system should be used for viewing and processing unless
        a use case dictates otherwise
        """
        return self.coordinateSystems[0]

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
        if output_cs_names.pop() is None:
            raise ValueError("Output coordinate system cannot be None.")
        return data

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
            if transformation.type == "scale":
                dim = transformation.ndim
            else:
                assert transformation.type == "sequence" and isinstance(
                    transformation.transformations[0], VectorScale
                )
                dim = transformation.transformations[0].ndim
            dims.append(dim)
        if len(set(dims)) > 1:
            raise ValueError(
                "All `Dataset` instances of a `Multiscale` must have the same "
                f"dimensionality. Got {dims}."
            )
        return datasets

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
                assert transform.type == "sequence" and isinstance(
                    transform.transformations[0], VectorScale
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
                    f"than dataset {i+1} (scales = {s2})."
                )
        return datasets

    @model_validator(mode="after")
    def check_cs_input_output(self) -> Self:
        """Check input and output for each coordinate system.

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
