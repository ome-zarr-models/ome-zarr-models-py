from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models.v04.labels import LabelsAttrs

__all__ = ["Labels", "LabelsAttrs"]


class Labels(GroupSpec[BaseOMEAttrs[LabelsAttrs], ArraySpec | GroupSpec], BaseGroupv05):  # type: ignore[misc]
    """
    An OME-Zarr labels dataset.
    """
