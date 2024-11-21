from dataclasses import Field, dataclass, asdict, field
from typing import Any, Mapping, Sequence

from typing import Literal

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
    type: Literal["scale"] = field(default="scale", init=False)
    scale: Sequence[float]

@dataclass(frozen=True, slots=True, kw_only=True)
class TranslationTransform:
    type: Literal["translation"] = field(default="translation", init=False)
    translation: Sequence[float]

@dataclass(frozen=True, slots=True, kw_only=True)
class Dataset:
    path: str
    coordinateTransformations: tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str]

@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleMetadata:
    """
    Link to the spec

    Attributes
    ----------
    axes : Sequence[Axis], Must be between 2 and 5, 
    ...
    """
    axes: tuple[Axis,Axis] | tuple[Axis,Axis,Axis] | tuple[Axis,Axis,Axis,Axis] | tuple[Axis,Axis,Axis,Axis,Axis]
    datasets: Sequence[Dataset]
    coordinateTransformations: tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str] | None
    name: Any | None = None
    version: Any = None
    metadata: Mapping[str, Any] | None = None
    type: Any | None = None

@dataclass(frozen=True, slots=True, kw_only=True)
class ChannelWindow:
    end: float
    max: float
    min: float
    start: float

@dataclass(frozen=True, slots=True, kw_only=True)
class Channel:
    window: ChannelWindow
    label: str | None = None
    family: str | None = None
    color: str | None = None
    active: bool | None = None

@dataclass(frozen=True, slots=True, kw_only=True)
class Omero:
    channels: Sequence[Channel]

@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleGroupAttributes:
    multiscales: Sequence[MultiscaleMetadata]
    omero: Any = None

@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleGroup(Group):
    attributes: MultiscaleGroupAttributes