import warnings
from collections.abc import Sequence
from typing import Self

import zarr
from pydantic import Field
from pydantic_zarr.v3 import GroupSpec

from ome_zarr_models._utils import TransformGraph, _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs, BaseZarrAttrs
from ome_zarr_models._v06.coordinate_transforms import (
    AnyTransform,
    CoordinateSystem,
    CoordinateSystemIdentifier,
)
from ome_zarr_models._v06.image import Image


class CollectionAttrs(BaseOMEAttrs):
    coordinateTransformations: tuple[AnyTransform, ...] = Field(default=())
    coordinateSystems: tuple[CoordinateSystem, ...] = Field(default=())

    def get_group_paths(self) -> dict[str, type[Image]]:  # type: ignore[override]
        coord_sys_names = [c.name for c in self.coordinateSystems]
        paths = {}
        for transform in self.coordinateTransformations:
            for coordinate_system in (transform.input, transform.output):
                if isinstance(coordinate_system, CoordinateSystemIdentifier):
                        paths[coordinate_system.path] = Image
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

    @classmethod
    def new(
        cls,
        *,
        images: dict[str, Image],
        coord_transforms: Sequence[AnyTransform] = (),
        coord_systems: Sequence[CoordinateSystem] = (),
    ) -> "Collection":
        """
        Create a new `Collection` from a sequence of images and coordinate metadata.

        Parameters
        ----------
        images :
            A dictionary mapping image names to Image objects. The keys are the paths
            to the images within the collection group.
        coord_transforms :
            Coordinate transforms to add to this collection.
        coord_systems :
            Coordinate systems to add to this collection.

        Notes
        -----
        This class does not store or copy any array data. To save array data,
        first write this class to a Zarr store, and then write data to the Zarr
        arrays in that store.
        """
        members_flat = {}
        for name, image in images.items():
            base_path = "/" + name.lstrip("/")
            # Get the flattened representation of the image
            image_flat = image.to_flat(root_path=base_path)
            # Merge into the collection's flat dict
            members_flat.update(image_flat)

        return Collection(
            members=GroupSpec.from_flat(members_flat).members,
            attributes=BaseZarrAttrs(
                ome=CollectionAttrs(
                    coordinateTransformations=tuple(coord_transforms),
                    coordinateSystems=tuple(coord_systems),
                    version="0.6",
                )
            ),
        )

    @property
    def images(self) -> dict[str, Image]:
        """
        Mapping from path to image.
        """
        if self.members is None:
            return {}

        images = {}
        for member_name, member in self.members.items():
            if not isinstance(member, GroupSpec):
                warnings.warn(
                    f"Member '{member_name}' is an array, not an OME-Zarr image",
                    stacklevel=2,
                )
                continue
            images[member_name] = Image(
                attributes=member.attributes, members=member.members
            )
        return images

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
