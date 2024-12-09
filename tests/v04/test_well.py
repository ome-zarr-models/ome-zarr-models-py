import json
from pathlib import Path

import pytest
from pydantic import BaseModel
from tests.v04.conftest import read_in_json

from ome_zarr_models.v04.well import Well, WellImage


def check_against_json(json_path: Path, expected_model: BaseModel) -> None:
    with open(json_path) as f:
        data = json.load(f)

    assert type(expected_model)(**data["well"]) == expected_model


@pytest.mark.parametrize(
    ("filename", "model_expected"),
    [
        (
            "well_example_1.json",
            Well(
                images=[
                    WellImage(path="0", acquisition=1),
                    WellImage(path="1", acquisition=1),
                    WellImage(path="2", acquisition=2),
                    WellImage(path="3", acquisition=2),
                ],
                version="0.4",
            ),
        ),
        (
            "well_example_2.json",
            Well(
                images=[
                    WellImage(path="0", acquisition=0),
                    WellImage(path="1", acquisition=3),
                ],
                version="0.4",
            ),
        ),
    ],
)
def test_examples_valid(filename: str, model_expected: Well) -> None:
    model = read_in_json(json_fname=filename, model_cls=Well)
    assert model == model_expected


def test_get_paths():
    well = Well(
        images=[
            WellImage(path="0", acquisition=1),
            WellImage(path="1", acquisition=1),
            WellImage(path="2", acquisition=2),
            WellImage(path="3", acquisition=2),
        ],
        version="0.4",
    )

    assert well.get_acquisition_paths() == {1: ["0", "1"], 2: ["2", "3"]}
