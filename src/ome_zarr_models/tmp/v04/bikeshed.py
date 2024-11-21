"""
Pydantic models related to OME-NGFF 0.4 specs, as implemented in
fractal-tasks-core.
"""
import logging
from typing import Optional
from typing import TypeVar
from typing import Union

from pydantic import Field
from pydantic import field_validator

from ome_zarr_models.base import Base
from ome_zarr_models.utils import unique_items_validator
from ome_zarr_models.zarr_models.v04.multiscales import Dataset


logger = logging.getLogger(__name__)


T = TypeVar("T")

class Axis(Base):
    """
    Model for an element of `Multiscale.axes`.

    See https://ngff.openmicroscopy.org/0.4/#axes-md.
    """

    name: str
    type: str | None = None
    unit: str | None = None


class ImageInWell(Base):
    """
    Model for an element of `Well.images`.

    **Note 1:** The NGFF image is defined in a different model
    (`NgffImageMeta`), while the `Image` model only refere to an item of
    `Well.images`.

    **Note 2:** We deviate from NGFF specs, since we allow `path` to be an
    arbitrary string.
    TODO: include a check like `constr(regex=r'^[A-Za-z0-9]+$')`, through a
    Pydantic validator.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    acquisition: int | None = Field(
        None, description="A unique identifier within the context of the plate"
    )
    path: str = Field(
        ..., description="The path for this field of view subgroup"
    )


class Well(Base):
    """
    Model for `NgffWellMeta.well`.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    images: list[ImageInWell] = Field(
        ..., description="The images included in this well", min_length=1
    )
    version: str | None = Field(
        None, description="The version of the specification"
    )
    _check_unique = field_validator("images")(unique_items_validator)


class NgffWellMeta(Base):
    """
    Model for the metadata of a NGFF well.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    well: Well | None = None

    def get_acquisition_paths(self) -> dict[int, list[str]]:
        """
        Create mapping from acquisition indices to corresponding paths.

        Runs on the well zarr attributes and loads the relative paths in the
        well.

        Returns:
            Dictionary with `(acquisition index: [image_path])` key/value
            pairs.

        Raises:
            ValueError:
                If an element of `self.well.images` has no `acquisition`
                    attribute.
        """
        acquisition_dict = {}
        for image in self.well.images:
            if image.acquisition is None:
                raise ValueError(
                    "Cannot get acquisition paths for Zarr files without "
                    "'acquisition' metadata at the well level"
                )
            if image.acquisition not in acquisition_dict:
                acquisition_dict[image.acquisition] = []
            acquisition_dict[image.acquisition].append(image.path)
        return acquisition_dict


######################
# Plate models
######################


class AcquisitionInPlate(Base):
    """
    Model for an element of `Plate.acquisitions`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    id: int = Field(
        description="A unique identifier within the context of the plate"
    )
    maximumfieldcount: int | None = Field(
        None,
        description=(
            "Int indicating the maximum number of fields of view for the "
            "acquisition"
        ),
    )
    name: str | None = Field(
        None, description="a string identifying the name of the acquisition"
    )
    description: str | None = Field(
        None,
        description="The description of the acquisition",
    )
    # TODO: Add starttime & endtime
    # starttime: str | None = Field()
    # endtime: str | None = Field()


class WellInPlate(Base):
    """
    Model for an element of `Plate.wells`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    path: str
    rowIndex: int
    columnIndex: int


class ColumnInPlate(Base):
    """
    Model for an element of `Plate.columns`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    name: str


class RowInPlate(Base):
    """
    Model for an element of `Plate.rows`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    name: str


class Plate(Base):
    """
    Model for `NgffPlateMeta.plate`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    acquisitions: list[AcquisitionInPlate] | None = None
    columns: list[ColumnInPlate]
    field_count: int | None = None
    name: str | None = None
    rows: list[RowInPlate]
    # version will become required in 0.5
    version: str | None = Field(
        None, description="The version of the specification"
    )
    wells: list[WellInPlate]


class NgffPlateMeta(Base):
    """
    Model for the metadata of a NGFF plate.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    plate: Plate