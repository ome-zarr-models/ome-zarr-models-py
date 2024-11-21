from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Self

AxisType = Literal["time", "space", "channel"]


class ToFromJSON(ABC):
    """A class that can serialise to and from JSON."""

    @classmethod
    @abstractmethod
    def _from_json(cls, json: dict) -> Self: ...


# TODO: decide if slots is future-proof w.r.t. dynamic data like OMERO
@dataclass(frozen=True, slots=True, kw_only=True)
class Axis(ToFromJSON):
    """
    A single axis.

    Parameters
    ----------
    name : Axis name.
    type : Axis type.
    unit : Axis unit.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#axes-md
    """

    name: str
    type: AxisType | Any | None = None
    # TODO: decide how to handle SHOULD fields, e.g. by raising a warning
    unit: str | None = None

    @classmethod
    def _from_json(cls, json: dict) -> Self:
        name = json["name"]
        type_ = json.get("type", None)
        unit = json.get("unit", None)
        return cls(name=name, type=type_, unit=unit)


@dataclass(frozen=True, slots=True, kw_only=True)
class ScaleTransform(ToFromJSON):
    """
    An scale transform.

    Parameters
    ----------
    type : Transform type.
    scale : Scale factor.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#trafo-md
    """

    type: Literal["scale"]
    scale: Sequence[float]

    @classmethod
    def _from_json(cls, json: dict) -> Self:
        return cls(type="scale", scale=json["scale"])


@dataclass(frozen=True, slots=True, kw_only=True)
class TranslationTransform(ToFromJSON):
    """
    A translation transform.

    Parameters
    ----------
    type : Transform type.
    translation : Translation vector.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#trafo-md
    """

    type: Literal["translation"]
    translation: Sequence[float]

    @classmethod
    def _from_json(cls, json: dict) -> Self:
        return cls(type="translation", translation=json["translation"])


@dataclass(frozen=True, slots=True, kw_only=True)
class CoordinateTransforms:
    """
    A class to represent allowed coordinate transforms.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#trafo-md
    """

    scale: ScaleTransform
    translation: TranslationTransform | None

    @classmethod
    def _from_json(cls, json: list):
        scale = ScaleTransform._from_json(json[0])
        if len(json) == 2:
            translation = TranslationTransform._from_json(json[1])
        else:
            translation = None
        return cls(scale=scale, translation=translation)


@dataclass(frozen=True, slots=True, kw_only=True)
class Dataset(ToFromJSON):
    """
    A single dataset.

    Parameters
    ----------
    path :
        Path to dataset.
    coordinateTransformations :
        Coordinate transformations for dataset.

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#multiscale-md
    """

    path: str
    coordinateTransformations: CoordinateTransforms

    @classmethod
    def _from_json(cls, json) -> Self:
        path = json["path"]
        transforms = CoordinateTransforms._from_json(json["coordinateTransformations"])
        return cls(path=path, coordinateTransformations=transforms)


@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleMetadata(ToFromJSON):
    """
    Multiscale metadata.

    Attributes
    ----------
    axes : Sequence[Axis]
        Must be between 2 and 5,

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#multiscale-md
    """

    axes: (
        tuple[Axis, Axis]
        | tuple[Axis, Axis, Axis]
        | tuple[Axis, Axis, Axis, Axis]
        | tuple[Axis, Axis, Axis, Axis, Axis]
    )
    datasets: Sequence[Dataset]
    coordinateTransformations: CoordinateTransforms | None = None
    name: Any | None = None
    version: Any | None = None
    metadata: Mapping[str, Any] | None = None
    type: Any | None = None

    @classmethod
    def _from_json(cls, json: dict) -> Self:
        axes = tuple(Axis._from_json(v) for v in json["axes"])
        datasets = [Dataset._from_json(v) for v in json["datasets"]]
        if json["coordinateTransformations"] is None:
            transforms = None
        else:
            transforms = CoordinateTransforms._from_json(
                json["coordinateTransformations"]
            )
        name = json.get("name", None)
        version = json.get("version", None)
        metadata = json.get("metadata", None)
        type_ = json.get("type", None)

        return cls(
            axes=axes,
            datasets=datasets,
            coordinateTransformations=transforms,
            name=name,
            version=version,
            metadata=metadata,
            type=type_,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class MultiscaleMetadatas(ToFromJSON):
    """
    A set of multiscale images.

    Attributes
    ----------
    multiscales

    References
    ----------
    https://ngff.openmicroscopy.org/0.4/index.html#multiscale-md
    """

    multiscales: Sequence[MultiscaleMetadata]

    @classmethod
    def _from_json(cls, json: dict) -> Self:
        multiscales = [
            MultiscaleMetadata._from_json(val) for val in json["multiscales"]
        ]
        return cls(multiscales=multiscales)
