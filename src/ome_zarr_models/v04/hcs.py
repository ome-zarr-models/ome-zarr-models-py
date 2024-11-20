from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from ome_zarr_models.zarr_models.v2 import Group


######################
#
# Well models metadata
#
######################


@dataclass(frozen=True, slots=True, kw_only=True)
class WellImage:
    """See https://ngff.openmicroscopy.org/0.4/#well-md."""

    acquisition: int
    path: str


@dataclass(frozen=True, slots=True, kw_only=True)
class WellMetadata:
    """See https://ngff.openmicroscopy.org/0.4/#well-md."""

    images: Sequence[WellImage]
    version: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class WellGroup(Group):
    attributes: WellMetadata


######################
# Plate models
######################


@dataclass(frozen=True, slots=True, kw_only=True)
class Acquisition:
    """See https://ngff.openmicroscopy.org/0.4/#plate-md."""

    id: int
    name: str | None = None
    # Positive integer
    maximumfieldcount: int | None = None
    description: str | None = None
    starttime: int | None = None
    endtime: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Well:
    """See https://ngff.openmicroscopy.org/0.4/#plate-md."""

    path: str
    rowIndex: int
    columnIndex: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Column:
    """See https://ngff.openmicroscopy.org/0.4/#plate-md."""

    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Row:
    """See https://ngff.openmicroscopy.org/0.4/#plate-md."""

    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PlateMetadata:
    """See https://ngff.openmicroscopy.org/0.4/#plate-md."""

    columns: Sequence[Column]
    rows: Sequence[Row]
    wells: Sequence[Well]
    version: str
    acquisitions: Sequence[Acquisition] | None = None
    field_count: int | None = None
    name: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PlateGroup(Group):
    attributes: PlateMetadata
