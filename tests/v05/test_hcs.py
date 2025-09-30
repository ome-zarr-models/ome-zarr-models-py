from typing import TYPE_CHECKING

import zarr
from zarr.abc.store import Store

from ome_zarr_models.v05.hcs import HCS, HCSAttrs
from ome_zarr_models.v05.plate import Acquisition, Column, Plate, Row, WellInPlate
from tests.v05.conftest import json_to_zarr_group

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_hcs(store: Store) -> None:
    zarr_group = json_to_zarr_group(json_fname="hcs_example.json", store=store)
    ome_group = HCS.from_zarr(zarr_group)
    assert ome_group.attributes.ome == HCSAttrs(
        plate=Plate(
            acquisitions=[
                Acquisition(
                    id=1,
                    name="Meas_01(2012-07-31_10-41-12)",
                    maximumfieldcount=2,
                    description=None,
                    starttime=1343731272000,
                    endtime=None,
                ),
                Acquisition(
                    id=2,
                    name="Meas_02(201207-31_11-56-41)",
                    maximumfieldcount=2,
                    description=None,
                    starttime=1343735801000,
                    endtime=None,
                ),
            ],
            columns=[Column(name="1"), Column(name="2"), Column(name="3")],
            field_count=4,
            name="test",
            rows=[Row(name="A"), Row(name="B")],
            wells=[
                WellInPlate(path="A/1", rowIndex=0, columnIndex=0),
                WellInPlate(path="A/2", rowIndex=0, columnIndex=1),
                WellInPlate(path="A/3", rowIndex=0, columnIndex=2),
                WellInPlate(path="B/1", rowIndex=1, columnIndex=0),
                WellInPlate(path="B/2", rowIndex=1, columnIndex=1),
                WellInPlate(path="B/3", rowIndex=1, columnIndex=2),
            ],
            version="0.5",
        ),
        version="0.5",
    )
    well_groups = list(ome_group.well_groups)
    assert len(well_groups) == 0


def test_non_existent_wells() -> None:
    """
    Make sure it's possible to create a HCS that has well paths that don't exist
    as Zarr groups.

    The relevant part of the OME-Zarr specification (https://ngff.openmicroscopy.org/0.5/index.html#plate-md)
    does not specify explicitly that the Zarr groups have to exist.
    """
    HCS(
        attributes={
            "ome": {
                "plate": {
                    "acquisitions": [{"id": 1}, {"id": 2}, {"id": 3}],
                    "columns": [{"name": "1"}],
                    "field_count": 10,
                    "rows": [{"name": "A"}],
                    "version": "0.4",
                    "wells": [{"columnIndex": 0, "path": "A/1", "rowIndex": 0}],
                },
                "version": "0.5",
            }
        }
    )


def test_non_existent_wells_from_zarr() -> None:
    """
    Same as above, but using from_zarr(...)
    """

    plate: dict[str, JsonValue] = {
        "columns": [{"name": "1"}],
        "rows": [{"name": "A"}],
        "wells": [{"path": "A/1", "rowIndex": 0, "columnIndex": 0}],
        "version": "0.5",
    }
    group = group = zarr.create_group(
        store={},
        zarr_format=3,
        attributes={"ome": {"plate": plate, "version": "0.5"}},
    )
    HCS.from_zarr(group)
