from typing import Self

import zarr
from pydantic import Field, PrivateAttr

from ome_zarr_models._utils import _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
    Transform,
)
from ome_zarr_models._v06.image import Image


class ContainerAttrs(BaseOMEAttrs):
    coordinateTransformations: tuple[AnyTransform, ...] = Field(default=())
    coordinateSystems: tuple[CoordinateSystem, ...] = Field(default=())

    def get_group_paths(self) -> dict[str, type[Image]]:  # type: ignore[override]
        paths = {}
        for transform in self.coordinateTransformations:
            if transform.input is not None and transform.input.startswith("/"):
                paths[transform.input.removeprefix("/")] = Image

        return paths


class Container(BaseGroupv06[ContainerAttrs]):
    """
    An OME-Zarr container group.

    This is a group that stores a series of other multiscale images,
    along with additional coordinate transformations and coordinate systems.
    """

    _images: list[Image] = PrivateAttr(default=[])
    # List of all coordinate systems found within this container
    _all_systems: list[CoordinateSystem] = PrivateAttr(default=[])
    # List of all coordinate transformations found within this container
    _all_transforms: list[AnyTransform] = PrivateAttr(default=[])

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr image model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        self = _from_zarr_v3(group, cls, ContainerAttrs)
        self._all_systems.extend(self.ome_attributes.coordinateSystems)
        self._all_transforms.extend(self.ome_attributes.coordinateTransformations)
        return self

    @property
    def coordinate_systems(self) -> tuple[CoordinateSystem, ...]:
        """
        All coordinate systems in this container.
        """
        return tuple(self._all_systems)

    @property
    def coordinate_transforms(self) -> tuple[Transform, ...]:
        """
        All coordinate transformations in this container.
        """
        return tuple(self._all_transforms)
