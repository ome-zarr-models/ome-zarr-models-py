from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from ome_zarr_models.zarr_models.v2 import Group

AxisType = Literal["time", "space", "channel"]


# TODO: decide if slots is future-proof w.r.t. dynamic data like OMERO
@dataclass(frozen=True, slots=True, kw_only=True)
class Axis:
    type: AxisType | Any | None = None
    name: str
    # TODO: decide how to handle SHOULD fields, e.g. by raising a warning
    unit: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ScaleTransform:
    type: Literal["scale"]
    scale: Sequence[float]



@dataclass(frozen=True, slots=True, kw_only=True)
class TranslationTransform:
    type: Literal["translation"]
    translation: Sequence[float]



@dataclass(frozen=True, slots=True, kw_only=True)
class Dataset:
    path: str
    coordinateTransformations: (
        tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str]
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleMetadata:
    """
    A dataclass representing metadata in v0.4 of the OME-NGFF specification.

    Attributes
    ----------
    axes : Sequence[Axis], Must be between 2 and 5,
    ...
    """

    axes: (
        tuple[Axis, Axis]
        | tuple[Axis, Axis, Axis]
        | tuple[Axis, Axis, Axis, Axis]
        | tuple[Axis, Axis, Axis, Axis, Axis]
    )
    datasets: Sequence[Dataset]
    coordinateTransformations: (
        tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str] | None
    )
    name: Any | None = None
    version: Any = None
    metadata: Mapping[str, Any] | None = None
    type: Any | None = None



@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleGroupAttributes:
    multiscales: Sequence[MultiscaleMetadata]
    omero: Any



@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleGroup(Group):
    attributes: MultiscaleGroupAttributes
