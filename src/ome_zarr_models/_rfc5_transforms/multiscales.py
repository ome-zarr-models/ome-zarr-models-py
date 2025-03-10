from __future__ import annotations

from typing import Self

from pydantic import (
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
)
from ome_zarr_models.base import BaseAttrs

__all__ = ["Dataset"]


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    path: str
    coordinateTransformations: tuple[CoordinateTransformation] = Field(
        ..., min_length=1, max_length=1
    )

    @field_validator("coordinateTransformations", mode="after")
    @classmethod
    def _ensure_transform_dimensionality(
        cls,
        transforms: tuple[CoordinateTransformation],
    ) -> tuple[CoordinateTransformation]:
        """
        Ensures that the input transform
        1) is either a single scale, a single translation or a sequence of a scale and
        a translation (in this order)
        2) if a sequence, the scale and translation have the same dimensionality
        """
        # TODO: implement
        # vector_transforms = filter(
        #     lambda v: isinstance(v, VectorTransform), transforms
        # )
        # ndims = tuple(map(_ndim, vector_transforms))  # type: ignore[arg-type]
        # ndims_set = set(ndims)
        # if len(ndims_set) > 1:
        #     msg = (
        #         "The transforms have inconsistent dimensionality. "
        #         f"Got transforms with dimensionality = {ndims}."
        #     )
        #     raise ValueError(msg)
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

    # TODO: to be replaced by a more general validator for checking the consistency
    #  of all the "global" coordinate transformations
    # @model_validator(mode="after")
    # def _ensure_axes_top_transforms(data: Self) -> Self:
    #     """
    #     Ensure that the length of the axes matches the dimensionality of the
    #     transforms defined in the top-level coordinateTransformations, if present.
    #     """
    #     self_ndim = len(data.axes)
    #     if data.coordinateTransformations is not None:
    #         for tx in data.coordinateTransformations:
    #             if hasattr(tx, "ndim") and self_ndim != tx.ndim:
    #                 msg = (
    #                     f"The length of axes does not match the dimensionality of "
    #                     f"the {tx.type} transform in coordinateTransformations. "
    #                     f"Got {self_ndim} axes, but the {tx.type} transform has "
    #                     f"dimensionality {tx.ndim}"
    #                 )
    #                 raise ValueError(msg)
    #     return data

    @model_validator(mode="after")
    def _ensure_same_output_cs_for_all_datasets(data: Self) -> Self:
        """
        Ensure that all datasets have the same output coordinate system.
        """
        # TODO: new implementation
        # self_ndim = len(data.axes)
        # for ds_idx, ds in enumerate(data.datasets):
        #     for tx in ds.coordinateTransformations:
        #         if hasattr(tx, "ndim") and self_ndim != tx.ndim:
        #             msg = (
        #                 f"The length of axes does not match the dimensionality of "
        #                 f"the {tx.type} transform in "
        #                 f"datasets[{ds_idx}].coordinateTransformations. "
        #                 f"Got {self_ndim} axes, but the {tx.type} transform has "
        #                 f"dimensionality {tx.ndim}"
        #             )
        #             raise ValueError(msg)
        return data

    @field_validator("datasets", mode="after")
    @classmethod
    def _ensure_ordered_scales(cls, datasets: list[Dataset]) -> list[Dataset]:
        """
        Make sure datasets are ordered from highest resolution to smallest.
        """
        # TODO: reimplement
        # scale_transforms = [d.coordinateTransformations[0] for d in datasets]
        # # Only handle scales given in metadata, not in files
        # scale_vector_transforms = [
        #     t for t in scale_transforms if isinstance(t, VectorScale)
        # ]
        # scales = [s.scale for s in scale_vector_transforms]
        # for i in range(len(scales) - 1):
        #     s1, s2 = scales[i], scales[i + 1]
        #     is_ordered = all(s1[j] <= s2[j] for j in range(len(s1)))
        #     if not is_ordered:
        #         raise ValueError(
        #             f"Dataset {i} has a lower resolution (scales = {s1}) "
        #             f"than dataset {i+1} (scales = {s2})."
        #         )

        return datasets
