from pydantic import Field

from ome_zarr_models.base import Base


class AcquisitionInPlate(Base):
    """
    Model for an element of `Plate.acquisitions`.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    id: int = Field(description="A unique identifier within the context of the plate")
    maximumfieldcount: int | None = Field(
        None,
        description=(
            "Int indicating the maximum number of fields of view for the " "acquisition"
        ),
    )
    name: str | None = Field(
        None, description="a string identifying the name of the acquisition"
    )
    description: str | None = Field(
        None,
        description="The description of the acquisition",
    )


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
    version: str | None = Field(None, description="The version of the specification")
    wells: list[WellInPlate]


class NgffPlateMeta(Base):
    """
    Model for the metadata of a NGFF plate.

    See https://ngff.openmicroscopy.org/0.4/#plate-md.
    """

    plate: Plate
