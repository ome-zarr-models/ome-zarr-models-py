from collections.abc import Generator
from typing import Self

from pydantic import model_validator

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.well import WellGroupNotFoundError
from ome_zarr_models.v04.base import BaseGroupv04
from ome_zarr_models.v04.plate import Plate
from ome_zarr_models.v04.well import Well

__all__ = ["HCS", "HCSAttrs"]


class HCSAttrs(BaseAttrs):
    """
    HCS metadtata attributes.
    """

    plate: Plate


class HCS(BaseGroupv04[HCSAttrs]):
    """
    An OME-Zarr high-content screening (HCS) dataset representing a single plate.
    """

    @model_validator(mode="after")
    def _check_valid_acquisitions(self) -> Self:
        """
        Check well acquisition IDs are in list of plate acquisition ids.
        """
        acquisitions = self.attributes.plate.acquisitions
        if acquisitions is None:
            return self

        valid_aq_ids = [aq.id for aq in acquisitions]

        for well_i, well_group in enumerate(self.well_groups):
            for image_i, well_image in enumerate(well_group.attributes.well.images):
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
        return len(self.attributes.plate.wells)

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
        WellGroupNotFoundError :
            If no Zarr group is found at the well path.
        """
        well = self.attributes.plate.wells[i]
        well_path = well.path
        well_path_parts = well_path.split("/")
        if len(well_path_parts) != 2:
            raise RuntimeError(f"Well path '{well_path_parts}' does not have two parts")
        row, col = well_path_parts
        if row not in self.members:
            raise WellGroupNotFoundError(
                f"Row '{row}' not found in group members: {self.members}"
            )
        if col not in self.members[row].members:
            raise WellGroupNotFoundError(
                f"Column '{col}' not found in row group members: {self.members[row]}"
            )
        group = self.members[row].members[col]
        return Well(attributes=group.attributes, members=group.members)
