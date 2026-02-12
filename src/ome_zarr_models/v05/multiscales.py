from __future__ import annotations

import warnings
from collections import Counter
from typing import TYPE_CHECKING, Any, Literal, Self, Union

from pydantic import (
    BaseModel,
    Field,
    JsonValue,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
    model_validator,
)

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.coordinate_transformations import (
    Transform,
    ValidTransform,
    VectorScale,
    VectorTransform,
    VectorTranslation,
    _build_transforms,
    _ndim,
)
from ome_zarr_models.common.validation import (
    check_length,
    check_ordered_scales,
    unique_items_validator,
)
from ome_zarr_models.exceptions import ValidationWarning
from ome_zarr_models.v05.axes import Axes

if TYPE_CHECKING:
    from collections.abc import Sequence
    from ome_zarr_models.v04.multiscales import Multiscale as MultiscaleV04


__all__ = ["Dataset", "Multiscale"]


VALID_NDIM = (2, 3, 4, 5)


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

    def to_version(
        self, version: Literal["0.4", "0.5"]
    ) -> Union["Multiscale", "MultiscaleV04"]:
        """
        Convert this Multiscale metadata to the specified version.

        Currently supported conversions are
        - 0.5 -> 0.4
        """
        if version == "0.5":
            return self
        elif version == "0.4":
            return self._to_v04()
        else:
            raise ValueError(f"Unsupported version conversion: 0.5 -> {version}")
        
    @classmethod
    def from_version(cls, multiscale: Union["MultiscaleV04", "Multiscale"]) -> "Multiscale":
        """
        Convert a Multiscale metadata from another version to this version.

        Currently supported conversions are
        - 0.4 -> 0.5
        """
        from ome_zarr_models.v04.multiscales import Multiscale as MultiscaleV04
        if isinstance(multiscale, Multiscale):
            return multiscale
        elif isinstance(multiscale, MultiscaleV04):
            return multiscale._to_v05()
        else:
            raise ValueError(
                f"Unsupported version conversion: {type(multiscale)} -> 0.5"
            )
        
    def _to_v04(self) -> "MultiscaleV04":
        from ome_zarr_models.v04.multiscales import (
            Multiscale as MultiscaleV04,
            Dataset as DatasetV04
        )
        from ome_zarr_models.v04.axes import Axis as AxisV04
        return MultiscaleV04(
            axes=tuple([AxisV04.model_validate(a.model_dump()) for a in self.axes]),
            datasets=tuple(
                DatasetV04(
                    path=d.path,
                    coordinateTransformations=d.coordinateTransformations,
                )
                for d in self.datasets
            ),
            coordinateTransformations=self.coordinateTransformations,
            metadata=self.metadata,
            name=self.name,
            type=self.type,
        )

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
        try:
            unique_items_validator(axis_names := [a.name for a in axes])
        except ValueError:
            raise ValueError(f"Axis names must be unique. Got {axis_names}") from None
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

        transform_types = tuple(t.type for t in transforms)
        if transform_types == ("scale",) or transform_types == ("scale", "translation"):
            return transforms_obj
        elif transform_types == ("translation", "scale"):
            if isinstance(transforms[0], VectorTranslation) and isinstance(
                transforms[1], VectorScale
            ):
                # Can only do the swap if we know the vectors
                warnings.warn(
                    "Translation and scale are in the wrong order "
                    "(scale should come first). Swapping transforms.",
                    ValidationWarning,
                    stacklevel=2,
                )
                new_transforms = (
                    transforms[1],
                    VectorTranslation(
                        type="translation",
                        translation=[
                            t * s
                            for t, s in zip(
                                transforms[0].translation,
                                transforms[1].scale,
                                strict=False,
                            )
                        ],
                    ),
                )
                return new_transforms

        raise ValueError(
            "Expected a scale or (scale, translation) transform. "
            f"Got {transform_types} instead."
        )

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
