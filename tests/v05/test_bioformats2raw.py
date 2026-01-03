import pytest
import zarr
from zarr.abc.store import Store

from ome_zarr_models.exceptions import ValidationWarning
from ome_zarr_models.v05.bioformats2raw import BioFormats2Raw, BioFormats2RawAttrs
from ome_zarr_models.v05.image import Image
from ome_zarr_models.v05.plate import (
    Acquisition,
    Column,
    Plate,
    Row,
    WellInPlate,
)
from tests.v05.conftest import json_to_zarr_group


def test_bioformats2raw_example_json(store: Store) -> None:
    zarr_group = json_to_zarr_group(
        json_fname="bioformats2raw_example.json", store=store
    )
    with pytest.warns(
        ValidationWarning, match="'version' field not specified in plate metadata"
    ):
        ome_group = BioFormats2Raw.from_zarr(zarr_group)

    assert ome_group.ome_attributes == BioFormats2RawAttrs(
        bioformats2raw_layout=3,
        version="0.5",
        plate=Plate(
            acquisitions=[
                Acquisition(id=0, maximumfieldcount=None, name=None, description=None)
            ],
            columns=[Column(name="1")],
            field_count=1,
            name="Plate Name 0",
            rows=[Row(name="A")],
            version="0.5",
            wells=[WellInPlate(path="A/1", rowIndex=0, columnIndex=0)],
        ),
        series=None,
    )


@pytest.mark.vcr
def test_bioformats2raw_get_image() -> None:
    zarr_grp = zarr.open_group(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0033A/BR00109990_C2.zarr",
        mode="r",
    )
    model = BioFormats2Raw.from_zarr(zarr_grp)
    assert model.ome_attributes == BioFormats2RawAttrs(
        version="0.5", bioformats2raw_layout=3, plate=None, series=None
    )
    assert model.image_paths == [str(i) for i in range(9)]
    assert list(model.images.keys()) == model.image_paths
    assert all(isinstance(v, Image) for v in model.images.values())
