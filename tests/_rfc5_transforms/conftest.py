import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from ome_zarr_models.base import BaseAttrs

T = TypeVar("T", bound=BaseAttrs)


def read_in_json(*, folder: str, json_fname: str, model_cls: type[T]) -> T:
    with open(Path(__file__).parent / folder / json_fname) as f:
        return model_cls.model_validate_json(f.read())


# paths are relative to the 'tests' directory
TESTS_FILE_TO_DATA_MAPPING = {
    "test_data_rfc5/from_specification/test_transformations.py": (
        "data_rfc5/from_specification/transformations"
    ),
    "test_data_rfc5/from_specification/test_subspace.py": (
        "data_rfc5/from_specification/subspace"
    ),
    "test_data_rfc5/from_specification/test_multiscales_strict.py": (
        "data_rfc5/from_specification/multiscales_strict"
    ),
    "test_data_rfc5/from_specification/test_coordinate_systems.py": (
        "data_rfc5/from_specification/coordinate_systems"
    ),
}


def get_data_folder(test_file: str) -> str:
    for file, folder in TESTS_FILE_TO_DATA_MAPPING.items():
        if test_file.endswith(file):
            return folder
    raise ValueError(f"Test file {test_file} not found in mapping.")


def _parse_data(folder: str, in_memory: T) -> Callable[..., Any]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            test_name = re.sub(r"^test_", "", func.__name__)
            model_cls = type(in_memory)
            parsed = read_in_json(
                folder=folder, json_fname=f"{test_name}.json", model_cls=model_cls
            )
            assert parsed == in_memory
            return func(*args, parsed=parsed, **kwargs)

        return inner

    return wrapper


def check_examples_rfc5_are_downloaded() -> None:
    if not Path("./data_rfc5/full_examples").exists():
        command = (
            "aws s3 --no-sign-request sync "
            "s3://ngff-rfc5-coordinate-transformation-examples/ "
            "tests/_rfc5_transforms/data_rfc5/full_examples/"
        )
        raise ValueError(
            "RFC5 full examples are not downloaded. Please run the following command "
            f"from the project root:\n{command}"
        )


check_examples_rfc5_are_downloaded()
