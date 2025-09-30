from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any, Literal, Self

from pydantic import (
    BaseModel,
    Field,
    JsonValue,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
    model_validator,
)

from ome_zarr_models._utils import duplicates
from ome_zarr_models._v06.axes import Axes
from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.coordinate_transformations import (
    ScaleTransform,
    Transform,
    TranslationTransform,
    VectorScale,
    VectorTransform,
    _build_transforms,
    _ndim,
)
from ome_zarr_models.common.validation import check_length, check_ordered_scales

if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = ["Dataset", "Multiscale"]


VALID_NDIM = (2, 3, 4, 5)
ValidTransform = tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform]


class Multiscale(BaseAttrs):
    """
    An element of multiscales metadata.
    """

    axes: Axes
    datasets: tuple[Dataset, ...] = Field(..., min_length=1)
    coordinateTransformations: ValidTransform | None = None
    metadata: JsonValue = None
    name: JsonValue | None = None
    type: JsonValue = None
    version: Literal["0.4"] | None = None

    @model_serializer(mode="wrap")
    def _serialize(
        self,
        serializer: SerializerFunctionWrapHandler,
    ) -> dict[str, Any]:
        d: dict[str, Any] = serializer(self)
        if self.coordinateTransformations is None:
            d.pop("coordinateTransformations", None)

        return d

    @property
    def ndim(self) -> int:
        """
        Dimensionality of the data described by this metadata.

        Determined by the length of the axes attribute.
        """
        return len(self.axes)

    @model_validator(mode="after")
    def _ensure_axes_top_transforms(data: Self) -> Self:
        """
        Ensure that the length of the axes matches the dimensionality of the transforms
        defined in the top-level coordinateTransformations, if present.
        """
        self_ndim = len(data.axes)
        if data.coordinateTransformations is not None:
            for tx in data.coordinateTransformations:
                if hasattr(tx, "ndim") and self_ndim != tx.ndim:
                    msg = (
                        f"The length of axes does not match the dimensionality of "
                        f"the {tx.type} transform in coordinateTransformations. "
                        f"Got {self_ndim} axes, but the {tx.type} transform has "
                        f"dimensionality {tx.ndim}"
                    )
                    raise ValueError(msg)
        return data

    @model_validator(mode="after")
    def _ensure_axes_dataset_transforms(data: Self) -> Self:
        """
        Ensure that the length of the axes matches the dimensionality of the transforms
        """
        self_ndim = len(data.axes)
        for ds_idx, ds in enumerate(data.datasets):
            for tx in ds.coordinateTransformations:
                if hasattr(tx, "ndim") and self_ndim != tx.ndim:
                    msg = (
                        f"The length of axes does not match the dimensionality of "
                        f"the {tx.type} transform in "
                        f"datasets[{ds_idx}].coordinateTransformations. "
                        f"Got {self_ndim} axes, but the {tx.type} transform has "
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
        scale_transforms = [d.coordinateTransformations[0] for d in datasets]
        # Only handle scales given in metadata, not in files
        scale_vector_transforms = [
            t for t in scale_transforms if isinstance(t, VectorScale)
        ]
        check_ordered_scales(scale_vector_transforms)
        return datasets

    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_axis_length(cls, axes: Axes) -> Axes:
        """
        Ensures that there are between 2 and 5 axes (inclusive)
        """
        check_length(axes, valid_lengths=VALID_NDIM, variable_name="axes")
        return axes

    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_axis_types(cls, axes: Axes) -> Axes:
        """
        Ensures that the following conditions are true:

        - there are only 2 or 3 axes with type `space`
        - the axes with type `space` are last in the list of axes
        - there is only 1 axis with type `time`
        - there is only 1 axis with type `channel`
        - there is only 1 axis with a type that is not `space`, `time`, or `channel`
        """
        check_length(
            [ax for ax in axes if ax.type == "space"],
            valid_lengths=[2, 3],
            variable_name="space axes",
        )
        check_length(
            [ax for ax in axes if ax.type == "time"],
            valid_lengths=[0, 1],
            variable_name="time axes",
        )
        check_length(
            [ax for ax in axes if ax.type == "channel"],
            valid_lengths=[0, 1],
            variable_name="channel axes",
        )
        check_length(
            [ax for ax in axes if ax.type not in ["space", "time", "channel"]],
            valid_lengths=[0, 1],
            variable_name="custom axes",
        )

        axis_types = [ax.type for ax in axes]
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

        return axes

    @field_validator("axes", mode="after")
    @classmethod
    def _ensure_unique_axis_names(cls, axes: Axes) -> Axes:
        """
        Ensures that the names of the axes are unique.
        """
        name_dupes = duplicates(a.name for a in axes)
        if len(name_dupes) > 0:
            msg = (
                f"Axis names must be unique. Axis names {tuple(name_dupes.keys())} are "
                "repeated."
            )
            raise ValueError(msg)
        return axes


class Dataset(BaseAttrs):
    """
    An element of Multiscale.datasets.
    """

    # TODO: validate that path resolves to an actual zarr array
    # TODO: can we validate that the paths must be ordered from highest resolution to
    # smallest using scale metadata?
    path: str
    coordinateTransformations: ValidTransform

    @classmethod
    def build(
        cls, *, path: str, scale: Sequence[float], translation: Sequence[float] | None
    ) -> Self:
        """
        Construct a `Dataset` from a path, a scale, and a translation.
        """
        return cls(
            path=path,
            coordinateTransformations=_build_transforms(
                scale=scale, translation=translation
            ),
        )

    @field_validator("coordinateTransformations", mode="before")
    def _ensure_scale_translation(
        transforms_obj: object,
    ) -> object:
        """
        Ensures that
        - there are only 1 or 2 transforms.
        - the first element is a scale transformation
        - the second element, if present, is a translation transform
        """
        # This is used as a before validator - to help use, we use pydantic to first
        # cast the input (which can in general anything) into a set of transformations.
        # Then we check the transformations are valid.
        #
        # This is a bit convoluted, but we do it because the default pydantic error
        # messages are a mess otherwise

        class Transforms(BaseModel):
            transforms: list[Transform]

        transforms = Transforms(transforms=transforms_obj).transforms
        check_length(transforms, valid_lengths=[1, 2], variable_name="transforms")

        maybe_scale = transforms[0]
        if maybe_scale.type != "scale":
            msg = (
                "The first element of `coordinateTransformations` must be a scale "
                f"transform. Got {maybe_scale} instead."
            )
            raise ValueError(msg)
        if len(transforms) == 2:
            maybe_trans = transforms[1]
            if (maybe_trans.type) != "translation":
                msg = (
                    "The second element of `coordinateTransformations` must be a "
                    f"translation transform. Got {maybe_trans} instead."
                )
                raise ValueError(msg)

        return transforms_obj

    @field_validator("coordinateTransformations", mode="after")
    @classmethod
    def _ensure_transform_dimensionality(
        cls,
        transforms: ValidTransform,
    ) -> ValidTransform:
        """
        Ensures that the elements in the input sequence define transformations with
        identical dimensionality. If any of the transforms are defined with a path
        instead of concrete values, then no validation will be performed and the
        transforms will be returned as-is.
        """
        vector_transforms = filter(lambda v: isinstance(v, VectorTransform), transforms)
        ndims = tuple(map(_ndim, vector_transforms))  # type: ignore[arg-type]
        ndims_set = set(ndims)
        if len(ndims_set) > 1:
            msg = (
                "The transforms have inconsistent dimensionality. "
                f"Got transforms with dimensionality = {ndims}."
            )
            raise ValueError(msg)
        return transforms
