from typing import Self

import zarr

from ome_zarr_models._utils import _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
    Transform,
)


class ContainerAttrs(BaseOMEAttrs):
    coordinateTransformations: tuple[AnyTransform, ...]
    coordinateSystems: tuple[CoordinateSystem, ...]


class Container(BaseGroupv06[ContainerAttrs]):
    """
    An OME-Zarr image dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr image model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        return _from_zarr_v3(group, cls, ContainerAttrs)
