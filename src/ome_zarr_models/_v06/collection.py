from typing import Self

import zarr
from pydantic import Field

from ome_zarr_models._utils import TransformGraph, _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
)
from ome_zarr_models._v06.image import Image


class CollectionAttrs(BaseOMEAttrs):
    coordinateTransformations: tuple[AnyTransform, ...] = Field(default=())
    coordinateSystems: tuple[CoordinateSystem, ...] = Field(default=())

    def get_group_paths(self) -> dict[str, type[Image]]:  # type: ignore[override]
        coord_sys_names = [c.name for c in self.coordinateSystems]
        paths = {}
        for transform in self.coordinateTransformations:
            if transform.input is not None and transform.input not in coord_sys_names:
                paths[transform.input] = Image

        return paths


class Collection(BaseGroupv06[CollectionAttrs]):
    """
    An OME-Zarr container group.

    This is a group that stores a series of other multiscale images,
    along with additional coordinate transformations and coordinate systems.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr collection from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr image metadata.
        """
        return _from_zarr_v3(group, cls, CollectionAttrs)

    @property
    def images(self) -> dict[str, Image]:
        if self.members is None:
            return {}
        return {
            member: Image(
                attributes=self.members[member].attributes,
                members=self.members[member].members,
            )
            for member in self.members
        }

    def transform_graph(self) -> TransformGraph:
        """
        Create a coordinate transformation graph for this image.
        """
        graph = TransformGraph()

        # Coordinate systems
        for system in self.ome_attributes.coordinateSystems:
            graph.add_system(system)
        # Coordinate transforms
        for transform in self.ome_attributes.coordinateTransformations:
            graph.add_transform(transform)

        images = self.images
        for image_path in self.images:
            graph.add_subgraph(image_path, images[image_path].transform_graph())

        return graph
