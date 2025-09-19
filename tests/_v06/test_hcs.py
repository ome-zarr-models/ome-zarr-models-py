from zarr.abc.store import Store

from ome_zarr_models._v06.hcs import HCS, HCSAttrs
from ome_zarr_models._v06.plate import Acquisition, Column, Plate, Row, WellInPlate
from tests._v06.conftest import json_to_zarr_group


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
            version="0.6",
        ),
        version="0.6",
    )
    well_groups = list(ome_group.well_groups)
    assert len(well_groups) == 0
