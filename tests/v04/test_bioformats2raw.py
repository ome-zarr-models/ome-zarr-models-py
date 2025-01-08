from ome_zarr_models.v04._bioformats2raw import BioFormats2RawAttrs
from ome_zarr_models.v04.plate import (
    Acquisition,
    Column,
    Plate,
    Row,
    WellInPlate,
)
from tests.v04.conftest import read_in_json


def test_bioformats2raw_example_json() -> None:
    model = read_in_json(
        json_fname="bioformats2raw_example.json", model_cls=BioFormats2RawAttrs
    )

    assert model == BioFormats2RawAttrs(
        bioformats2raw_layout=3,
        plate=Plate(
            acquisitions=[
                Acquisition(id=0, maximumfieldcount=None, name=None, description=None)
            ],
            columns=[Column(name="1")],
            field_count=1,
            name="Plate Name 0",
            rows=[Row(name="A")],
            version="0.4",
            wells=[WellInPlate(path="A/1", rowIndex=0, columnIndex=0)],
        ),
        series=None,
    )
