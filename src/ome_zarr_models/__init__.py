from importlib.metadata import PackageNotFoundError, version

import zarr
from pydantic import ValidationError

import ome_zarr_models.v04.hcs
import ome_zarr_models.v04.image
import ome_zarr_models.v04.image_label
import ome_zarr_models.v04.labels
import ome_zarr_models.v04.well
from ome_zarr_models.base import BaseGroup
from ome_zarr_models.v04.base import BaseGroupv04

try:
    __version__ = version("ome_zarr_models")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"


_V04_groups: list[type[BaseGroupv04]] = [
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


def open_ome_zarr(group: zarr.Group) -> BaseGroup:
    """
    Create an ome-zarr-models object from an existing OME-Zarr group.

    This function will 'guess' which type of OME-Zarr data exists by
    trying to validate each group metadata definition against your data.
    If validation is successful, that data class is returned without
    trying any more.

    Parameters
    ----------
    group : zarr.Group
        Zarr group containing OME-Zarr data.
    """
    for group_cls in _V04_groups:
        try:
            return group_cls.from_zarr(group)  # type: ignore[no-any-return]
        except ValidationError:
            continue

    raise RuntimeError(f"Could not find any matches for group {group}")
