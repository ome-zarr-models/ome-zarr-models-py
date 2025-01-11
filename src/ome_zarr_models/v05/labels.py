from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.v04.labels import LabelsAttrs
from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs

__all__ = ["Labels", "LabelsAttrs"]


class OMELabelsAttrs(BaseOMEAttrs):
    ome: LabelsAttrs


class Labels(GroupSpec[OMELabelsAttrs, ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr labels dataset.
    """
