from ome_zarr_models.common.omero import Channel, Omero, Window
from tests.v04.conftest import read_in_json


def test_load_example_json() -> None:
    model = read_in_json(json_fname="omero_example.json", model_cls=Omero)

    assert model == Omero(
        channels=[
            Channel(
                color="0000FF",
                window=Window(max=65535.0, min=0.0, start=0.0, end=1500.0),
                active=True,
                coefficient=1,
                family="linear",
                inverted=False,
                label="LaminB1",
            )
        ],
        id=1,
        name="example.tif",
        version="0.4",
        rdefs={"defaultT": 0, "defaultZ": 118, "model": "color"},
    )
