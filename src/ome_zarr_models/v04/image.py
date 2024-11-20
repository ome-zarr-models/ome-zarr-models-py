from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from typing import Any, Literal, Self, get_args

AxisType = Literal["time", "space", "channel"]


class ToFromJSON:
    @classmethod
    def from_json(cls, json: dict) -> Self:
        attributes = {}
        for field in fields(cls):
            if isinstance(field.type, ToFromJSON):
                attributes[field.name] = field.from_json(json[field.name])
            # TODO: fix this crime against programming:
            elif str(field.type).startswith("collections.abc.Sequence"):
                attributes[field.name] = []
                item_type = get_args(field.type)[0]
                for v in json[field.name]:
                    attributes[field.name].append(item_type.from_json(v))
            else:
                attributes[field.name] = json[field.name]

        return cls(**attributes)


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
    coordinateTransformations: (
        tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str]
    )


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
    coordinateTransformations: (
        tuple[ScaleTransform] | tuple[ScaleTransform, TranslationTransform | str] | None
    )
    name: Any | None = None
    version: Any = None
    metadata: Mapping[str, Any] | None = None
    type: Any | None = None


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
