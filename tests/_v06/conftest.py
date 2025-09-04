from __future__ import annotations

import json
import re
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from ome_zarr_models._v06.axes import Axis
from ome_zarr_models._v06.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformation,
    VectorScale,
)
from ome_zarr_models._v06.multiscales import Dataset, Multiscale
from ome_zarr_models.base import BaseAttrs
from tests import conftest

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T", bound=BaseAttrs)

VERSION: Literal["0.6"] = "0.6"
json_to_dict = partial(conftest.json_to_dict, version=VERSION)
read_in_json = partial(conftest.read_in_json, version=VERSION)
json_to_zarr_group = partial(conftest.json_to_zarr_group, version=VERSION)


# explanation of these paths and the dictionary below:
# - we have external data that we want to test against, from different sources and
#   located in different folders
# - for each folder of data, we will have a single .py test file testing that data
# - to keep track of which test file goes with which data folder, we use the dict below
EXAMPLES_PATH = Path(__file__).parent.parent / "data/examples/v06"
NGFF_06_EXAMPLES_PATH = str(EXAMPLES_PATH / "ngff/examples")
RFC5_EXAMPLES_PATH = str(
    EXAMPLES_PATH / "ngff-rfc5-coordinate-transformation-examples/zarr2"
)
RFC5_TESTS_PATH = "test_data_rfc5/ngff_rfc5_coordinate_transformation_examples"
# paths are relative to the 'tests' directory
TESTS_FILE_TO_DATA_MAPPING = {
    # data from specs
    "test_data_rfc5/ngff/test_transformations.py": (
        f"{NGFF_06_EXAMPLES_PATH}/transformations"
    ),
    "test_data_rfc5/ngff/test_subspace.py": (f"{NGFF_06_EXAMPLES_PATH}/subspace"),
    "test_data_rfc5/ngff/test_multiscales_strict.py": (
        f"{NGFF_06_EXAMPLES_PATH}/multiscales_strict"
    ),
    "test_data_rfc5/ngff/test_coordSystems.py": (
        f"{NGFF_06_EXAMPLES_PATH}/coordSystems"
    ),
    # 2d examples
    f"{RFC5_TESTS_PATH}/test_2d_axis_dependent.py": (
        f"{RFC5_EXAMPLES_PATH}/2d/axis_dependent"
    ),
    f"{RFC5_TESTS_PATH}/test_2d_basic.py": (f"{RFC5_EXAMPLES_PATH}/2d/basic"),
    f"{RFC5_TESTS_PATH}/test_2d_basic_binary.py": (
        f"{RFC5_EXAMPLES_PATH}/2d/basic_binary"
    ),
    f"{RFC5_TESTS_PATH}/test_2d_nonlinear.py": (f"{RFC5_EXAMPLES_PATH}/2d/nonlinear"),
    f"{RFC5_TESTS_PATH}/test_2d_simple.py": (f"{RFC5_EXAMPLES_PATH}/2d/simple"),
    # 3d examples
    f"{RFC5_TESTS_PATH}/test_3d_axis_dependent.py": (
        f"{RFC5_EXAMPLES_PATH}/3d/axis_dependent"
    ),
    f"{RFC5_TESTS_PATH}/test_3d_basic.py": (f"{RFC5_EXAMPLES_PATH}/3d/basic"),
    f"{RFC5_TESTS_PATH}/test_3d_basic_binary.py": (
        f"{RFC5_EXAMPLES_PATH}/3d/basic_binary"
    ),
    f"{RFC5_TESTS_PATH}/test_3d_nonlinear.py": (f"{RFC5_EXAMPLES_PATH}/3d/nonlinear"),
    f"{RFC5_TESTS_PATH}/test_3d_simple.py": (f"{RFC5_EXAMPLES_PATH}/3d/simple"),
    # user stories
    f"{RFC5_TESTS_PATH}/test_user_stories.py": (f"{RFC5_EXAMPLES_PATH}/user_stories"),
}


def get_data_folder_for_current_tests_file(test_file: str) -> str:
    """
    Given the absolute path to a test file, returns the corresponding data folder.

    TESTS_FILE_TO_DATA_MAPPING is used to map test files to data folders.
    """
    path = Path(test_file)
    rel_path = path.relative_to(path.parents[2])
    for file, folder in TESTS_FILE_TO_DATA_MAPPING.items():
        if rel_path == Path(file):
            return folder
    raise ValueError(
        f"Test file {test_file} not found in mapping (key should be: {rel_path})"
    )


def _parse_data(
    folder: str, expected: T, wrap_into_multiscale: bool = False
) -> Callable[..., Any]:
    """
    Helper decorator for testing external JSON data against expected Pydantic models.

    This decorator is called with three arguments:
        - folder: The folder where the data to be tested is located.
        - expected: The expected Pydantic model instance that the parsed data should be
            equal to.
        - wrap_into_multiscale: Whether to wrap the JSON data into a multiscale
            object. This is needed only for tests where the JSON data does not
            represent a full multiscale object but only contains coordinate systems and
            transformations.

    The decorator performs the following steps:
        1. Derives the name of the data file to be tested from the test function name.
        2. Loads the corresponding JSON file from the specified folder.
        3. If `wrap_into_multiscale` is True, wraps the JSON data into the JSON data as
            if it was contained in a multiscale object.
        4. Parses the JSON data into a Pydantic model of the same type as `expected`.
        5. Asserts that the parsed model is equal to the `expected` model.
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            test_name = re.sub(r"^test_", "", func.__name__)
            model_cls = type(expected)
            file_path_json = Path(__file__).parent / folder / f"{test_name}.json"
            file_path_zarr = Path(__file__).parent / folder / f"{test_name}.zarr"
            d: dict[str, Any]
            if file_path_json.exists():
                d = json_to_dict(json_fname=str(file_path_json))
            elif file_path_zarr.exists():
                raise NotImplementedError(
                    "Currently only comparison against JSON examples is supported"
                )
            else:
                raise FileNotFoundError(
                    f"Neither {file_path_json} nor {file_path_zarr} exists."
                )
            if wrap_into_multiscale:
                assert model_cls is Multiscale
                d = wrap_json_dict_into_multiscale_dict(d)

            json_str = json.dumps(d)
            parsed = model_cls.model_validate_json(json_str)
            assert parsed == expected
            return func(*args, parsed=parsed, **kwargs)

        return inner

    return wrapper


COORDINATE_SYSTEM_NAME_FOR_TESTS = "coordinate_system_name_reserved_for_tests"


def wrap_json_dict_into_multiscale_dict(d: dict[str, Any]) -> dict[str, Any]:
    """
    Wraps a JSON dict of coord systems and transformations into a multiscale JSON dict.
    """
    extra_cs = {
        "name": COORDINATE_SYSTEM_NAME_FOR_TESTS,
        "axes": [{"name": "j"}, {"name": "i"}],
    }
    d["coordinateSystems"].append(extra_cs)
    wrapped = d | {
        "datasets": [
            {
                "path": "0",
                "coordinateTransformations": [
                    {
                        "type": "scale",
                        "scale": [1.0, 1.0],
                        "input": "/0",
                        "output": COORDINATE_SYSTEM_NAME_FOR_TESTS,
                    }
                ],
            }
        ]
    }
    return wrapped


def _gen_dataset(
    output_coordinate_system: str,
    scale_factors: list[float],
    path: str = "0",
) -> Dataset:
    """
    Helper function for wrap_coordinate_transformations_and_systems_into_multiscale.
    """
    return Dataset(
        path=path,
        coordinateTransformations=[
            VectorScale(
                scale=scale_factors,
                input=f"/{path}",
                output=output_coordinate_system,
            )
        ],
    )


def wrap_coordinate_transformations_and_systems_into_multiscale(
    coordinate_systems: tuple[CoordinateSystem, ...],
    coordinate_transformations: tuple[CoordinateTransformation, ...],
) -> Multiscale:
    """
    Wraps coordinate systems and transformations into a multiscale object.
    """
    extra_cs = CoordinateSystem(
        name=COORDINATE_SYSTEM_NAME_FOR_TESTS,
        axes=[
            Axis(name="j"),
            Axis(name="i"),
        ],
    )
    return Multiscale(
        coordinateTransformations=coordinate_transformations,
        coordinateSystems=(*coordinate_systems, extra_cs),
        datasets=(
            _gen_dataset(
                output_coordinate_system=COORDINATE_SYSTEM_NAME_FOR_TESTS,
                scale_factors=[1.0] * len(extra_cs.axes),
            ),
        ),
    )
