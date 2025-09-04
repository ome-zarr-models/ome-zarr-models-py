import importlib
import os
from pathlib import Path

import pytest

from tests._v06.conftest import TESTS_FILE_TO_DATA_MAPPING


@pytest.mark.parametrize("test_file, data_folder", TESTS_FILE_TO_DATA_MAPPING.items())
def test_all_files_have_functions(test_file: str, data_folder: str) -> None:
    """
    Ensures that for each external data file we have a test covering it.

    The external files are either in JSON or Zarr format and they are arranged in
    several folders. All the tests within for data within the same folder are grouped
    into a single test file (.py). The locations of these test files are specified as
    the keys of the TESTS_FILE_TO_DATA_MAPPING dictionary, and the values of the
    dictionary are the corresponding data folders.

    This function checks that for each JSON or Zarr file there is a corresponding test
    function in the associated test file.
    """
    json_files = [
        f
        for f in os.listdir(Path(__file__).parent.parent / data_folder)
        if f.endswith(".json") and not f.startswith(".")
    ]
    zarr_files = [
        f
        for f in os.listdir(Path(__file__).parent.parent / data_folder)
        if f.endswith(".zarr")
    ]
    assert len(json_files) + len(zarr_files) > 0, "No JSON or Zarr files found."
    assert (
        len(json_files) == 0 or len(zarr_files) == 0
    ), "Only one of JSON or Zarr files should be present."

    module = importlib.import_module(
        "tests._v06." + test_file.replace(".py", "").replace("/", ".")
    )
    test_functions = [name for name in module.__dir__() if name.startswith("test_")]

    missing_functions = []

    for json_file in json_files:
        test_name = f"test_{json_file.replace('.json', '')}"
        if test_name not in test_functions:
            missing_functions.append(json_file)
    for zarr_file in zarr_files:
        test_name = f"test_{zarr_file.replace('.zarr', '')}"
        if test_name not in test_functions:
            missing_functions.append(zarr_file)

    if missing_functions:
        print("Missing test functions for the following JSON/Zarr files:")
        for missing in missing_functions:
            print(f"- {missing}")
        raise AssertionError("Some test functions are missing.")
