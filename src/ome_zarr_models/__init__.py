from importlib.metadata import PackageNotFoundError, version
from typing import Any

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


def open_ome_zarr(group: zarr.Group) -> BaseGroup:
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

    Raises
    ------
    RuntimeError
        If the passed group cannot be validated with any of the OME-Zarr group models.
    """
    group_cls: type[BaseGroup]
    for group_cls in _V05_groups + _V04_groups:
        try:
            return group_cls.from_zarr(group)
        except Exception:
            continue

    raise RuntimeError(
        f"Could not successfully validate {group} with any OME-Zarr group models.\n"
        "\n"
        "If you know what type of group you are trying to open, using the "
        "<group class>.from_zarr() method will give you a more informative "
        "error message explaining why validation failed."
    )
