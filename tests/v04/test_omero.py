import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from ome_zarr_models.v04.omero import Channel, Omero, Window


def test_load_example_json() -> None:
    with open(Path(__file__).parent / "data" / "omero_example.json") as f:
        data = json.load(f)

    assert Omero(**data) == Omero(
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


def test_bad_colour() -> None:
    # Check that a non-hex colour raises a validation error
    expected_msg = re.escape("String should match pattern '[0-9a-fA-F]{6}'")
    with pytest.raises(ValidationError, match=expected_msg):
        Omero(
            channels=[
                Channel(
                    color="0000FP",
                    window=Window(max=65535.0, min=0.0, start=0.0, end=1500.0),
                )
            ],
        )
