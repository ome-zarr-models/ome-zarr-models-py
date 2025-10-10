from __future__ import annotations

from typing import Self

from pydantic import (
    BaseModel,
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
    Scale,
    Sequence,
    # Transform,
    Translation,
)
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import (
    check_length,
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

        Determined by the number of dimensions of the output coordinate system.
        """
        output_cs_name = self.datasets[0].coordinateTransformations[0].output
        for cs in self.coordinateSystems:
            if cs.name == output_cs_name:
                return cs.ndim

        raise RuntimeError(
            f"Did not find coordinate system named '{output_cs_name}' in "
            "multiscales coordinate systems."
        )

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


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    # TODO: validate that path resolves to an actual zarr array
    # TODO: can we validate that the paths must be ordered from highest resolution to
    # smallest using scale metadata?
    path: str
    coordinateTransformations: tuple[AnyTransform, ...] = Field(
        ..., min_length=1, max_length=1
    )

    # TODO: introduce a .build(...) method, similar to the one in v05

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
            transforms: tuple[AnyTransform, ...]

        transforms = Transforms(transforms=transforms_obj).transforms
        check_length(transforms, valid_lengths=[1], variable_name="transforms")

        transform = transforms[0]
        if isinstance(transform, Sequence):
            check_length(
                transform.transformations,
                valid_lengths=[2],
                variable_name="transform.transforms (i.e. transformations composing "
                "the sequence)",
            )
            first, second = transform.transformations
            if not isinstance(first, Scale):
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
        transforms: tuple[AnyTransform, ...],
    ) -> tuple[AnyTransform, ...]:
        """
        Ensures that the dimensionality of the scale and translation (when both present)
        match
        """
        # this test will not be needed anymore when
        # https://github.com/ome-zarr-models/ome-zarr-models-py/issues/188 is addressed
        maybe_sequence = transforms[0]
        if isinstance(maybe_sequence, Sequence):
            first, second = maybe_sequence.transformations
            if (
                isinstance(first, Scale)
                and isinstance(second, Translation)
                and first.ndim != second.ndim
            ):
                raise ValueError(
                    "The length of the scale and translation vectors must be the same. "
                    f"Got {first.ndim} and {second.ndim}."
                )
        return transforms
