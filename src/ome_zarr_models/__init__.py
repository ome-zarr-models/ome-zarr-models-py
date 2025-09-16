from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any, Literal

import zarr

import ome_zarr_models.v04.hcs
import ome_zarr_models.v04.image
import ome_zarr_models.v04.image_label
import ome_zarr_models.v04.labels
import ome_zarr_models.v04.well
import ome_zarr_models.v05.hcs
import ome_zarr_models.v05.image
import ome_zarr_models.v05.image_label
import ome_zarr_models.v05.labels
import ome_zarr_models.v05.well
from ome_zarr_models.base import BaseGroup
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v05.base import BaseGroupv05

try:
    __version__ = version("ome_zarr_models")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

if TYPE_CHECKING:
    from collections.abc import Sequence

_V04_groups: list[type[BaseGroupv04[Any]]] = [
    ome_zarr_models.v04.hcs.HCS,
    # Important that ImageLabel is higher than Image
    # otherwise Image will happily parse an ImageLabel
    # dataset without parsing the image-label bit of
    # metadata
    ome_zarr_models.v04.image_label.ImageLabel,
    ome_zarr_models.v04.image.Image,
    ome_zarr_models.v04.labels.Labels,
    ome_zarr_models.v04.well.Well,
]

_V05_groups: list[type[BaseGroupv05[Any]]] = [
    ome_zarr_models.v05.hcs.HCS,
    # Important that ImageLabel is higher than Image
    # otherwise Image will happily parse an ImageLabel
    # dataset without parsing the image-label bit of
    # metadata
    ome_zarr_models.v05.image_label.ImageLabel,
    ome_zarr_models.v05.image.Image,
    ome_zarr_models.v05.labels.Labels,
    ome_zarr_models.v05.well.Well,
]


def open_ome_zarr(
    group: zarr.Group, *, version: Literal["0.4", "0.5"] | None = None
) -> BaseGroup:
    """
    Create an ome-zarr-models object from an existing OME-Zarr group.

    This function will 'guess' which type of OME-Zarr data exists by
    trying to validate each group metadata definition against your data.
    If validation is successful, that data class is returned without
    trying any more.

    It tries more recent versions of OME-Zarr first.

    Parameters
    ----------
    group : zarr.Group
        Zarr group containing OME-Zarr data.
    version : Literal['0.4', '0.5'], optional
        If you know which version of OME-Zarr your data is, you can
        specify it here. If not specified, all versions will be tried.
        The default is None, which means all versions will be tried.

    Raises
    ------
    RuntimeError
        If the passed group cannot be validated with any of the OME-Zarr group models.

    Warnings
    --------
    This will try and load your data with every version of every OME-Zarr group type,
    until a match is found. If data access is slow (e.g., in a remote store), this may
    take a long time. It will be quicker to directly use the OME-Zarr group class if you
    know which version and group you expect.
    """
    # because 'from_zarr' isn't defined on a shared super-class, list all variants here
    groups: Sequence[type[BaseGroupv05[Any] | BaseGroupv04[Any]]]
    match version:
        case None:
            groups = [*_V05_groups, *_V04_groups]
        case "0.4":
            groups = _V04_groups
        case "0.5":
            groups = _V05_groups
        case _:
            _versions = ("0.4", "0.5")  # type: ignore[unreachable]
            raise ValueError(
                f"Unsupported version '{version}', must be one of {_versions}, or None"
            )

    errors: list[Exception] = []
    for group_cls in groups:
        try:
            return group_cls.from_zarr(group)
        except Exception as e:
            errors.append(e)

    raise RuntimeError(
        f"Could not successfully validate {group} against any OME-Zarr group model.\n"
        "\n"
        "The following errors were encountered while trying to validate:\n\n"
        + "\n\n".join(f"- {type(e).__name__}: {e}" for e in errors)
    )
