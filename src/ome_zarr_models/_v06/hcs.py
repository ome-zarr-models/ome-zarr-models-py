from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Self

# Import needed for pydantic type resolution
import pydantic_zarr  # noqa: F401
import zarr
from pydantic import model_validator
from pydantic_zarr.v3 import GroupSpec

from ome_zarr_models._utils import _from_zarr_v3
from ome_zarr_models._v06.base import BaseGroupv06, BaseOMEAttrs
from ome_zarr_models._v06.plate import Plate
from ome_zarr_models._v06.well import Well
from ome_zarr_models.common.well import WellGroupNotFoundError

if TYPE_CHECKING:
    from pydantic_zarr.v3 import AnyGroupSpec

__all__ = ["HCS", "HCSAttrs"]


class HCSAttrs(BaseOMEAttrs):
    """
    HCS metadtata attributes.
    """

    plate: Plate

    def get_optional_group_paths(self) -> dict[str, type[Well]]:  # type: ignore[override]
        return {well.path: Well for well in self.plate.wells}


class HCS(BaseGroupv06[HCSAttrs]):
    """
    An OME-Zarr high content screening (HCS) dataset.
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
        hcs = _from_zarr_v3(group, cls, HCSAttrs)
        # Traverse all the Well groups, which themselves contain Image groups
        hcs_flat = hcs.to_flat()
        for well in hcs.ome_attributes.plate.wells:
            if well.path in group:
                well_group = group[well.path]
                well_group_flat = Well.from_zarr(well_group).to_flat()  # type: ignore[arg-type]
                for path in well_group_flat:
                    hcs_flat["/" + well.path + path] = well_group_flat[path]

        hcs_unflat: AnyGroupSpec = GroupSpec.from_flat(hcs_flat)
        return cls(attributes=hcs_unflat.attributes, members=hcs_unflat.members)

    @model_validator(mode="after")
    def _check_valid_acquisitions(self) -> Self:
        """
        Check well acquisition IDs are in list of plate acquisition ids.
        """
        acquisitions = self.ome_attributes.plate.acquisitions
        if acquisitions is None:
            return self

        valid_aq_ids = [aq.id for aq in acquisitions]

        for well_i, well_group in enumerate(self.well_groups):
            for image_i, well_image in enumerate(well_group.ome_attributes.well.images):
                if well_image.acquisition is None:
                    continue
                elif well_image.acquisition not in valid_aq_ids:
                    msg = (
                        f"Acquisition ID '{well_image.acquisition} "
                        f"(found in well {well_i}, {image_i}) "
                        f"is not in list of plate acquisitions: {valid_aq_ids}"
                    )
                    raise ValueError(msg)

        return self

    @property
    def n_wells(self) -> int:
        """
        Number of wells.
        """
        return len(self.ome_attributes.plate.wells)

    @property
    def well_groups(self) -> Generator[Well, None, None]:
        """
        Well groups within this HCS group.

        Notes
        -----
        Only well groups that exist are returned. This can be less than the number
        of wells defined in the HCS metadata if some of the well Zarr groups don't
        exist.
        """
        for i in range(self.n_wells):
            try:
                yield self.get_well_group(i)
            except WellGroupNotFoundError:
                continue

    def get_well_group(self, i: int) -> Well:
        """
        Get a single well group.

        Parameters
        ----------
        i :
            Index of well group.

        Raises
        ------
        WellGroupNotFoundError
            If no Zarr group is found at the well path.
        """
        if self.members is None:
            raise RuntimeError("Zarr group has no members")

        well = self.ome_attributes.plate.wells[i]
        well_path = well.path
        well_path_parts = well_path.split("/")
        if len(well_path_parts) != 2:
            raise RuntimeError(f"Well path '{well_path_parts}' does not have two parts")
        row, col = well_path_parts
        if row not in self.members:
            raise WellGroupNotFoundError(
                f"Row '{row}' not found in group members: {self.members}"
            )
        if (
            not isinstance(row_group := self.members[row], GroupSpec)
            or not isinstance(row_group.members, Mapping)
            or col not in row_group.members
        ):
            raise WellGroupNotFoundError(
                f"Column '{col}' not found in row group members: {self.members[row]}"
            )
        group = row_group.members[col]
        return Well(attributes=group.attributes, members=group.members)
