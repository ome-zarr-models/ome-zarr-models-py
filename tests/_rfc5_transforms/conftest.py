import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import zarr

from ome_zarr_models._rfc5_transforms.axes import Axis
from ome_zarr_models._rfc5_transforms.coordinate_transformations import (
    CoordinateSystem,
    CoordinateTransformationType,
    Scale,
)
from ome_zarr_models._rfc5_transforms.multiscales import Dataset, Multiscale
from ome_zarr_models.base import BaseAttrs

T = TypeVar("T", bound=BaseAttrs)

COORDINATE_SYSTEM_NAME_FOR_TESTS = "coordinate_system_name_reserved_for_tests"


def json_to_zarr_group(*, json_fname: str) -> zarr.Group:
    """
    Create an empty Zarr group, and set attributes from a JSON file.
    """
    group = zarr.open_group(store=zarr.MemoryStore())
    with open(Path(__file__).parent / "data_rfc5" / json_fname) as f:
        attrs = json.load(f)

    group.attrs.put(attrs)
    return group


def get_data_file_path(*, folder: str, json_fname: str) -> Path:
    return Path(__file__).parent / folder / json_fname


def read_in_json(*, file_path: Path, model_cls: type[T]) -> T:
    with open(file_path) as f:
        d = json.load(f)
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

        wrapped_json = json.dumps(wrapped)

        return model_cls.model_validate_json(wrapped_json)


def read_in_zarr(*, file_path: Path, model_cls: type[T]) -> T:
    raise NotImplementedError(
        "The tests require NGFF 0.5 support since the data is the in Zarr v3 format. "
        "Tracked here https://github.com/ome-zarr-models/ome-zarr-models-py/issues/88"
    )


# paths are relative to the 'tests' directory
TESTS_FILE_TO_DATA_MAPPING = {
    # data from specs
    "test_data_rfc5/ngff/test_transformations.py": (
        "data_rfc5/ngff/0.6-dev/examples/transformations"
    ),
    "test_data_rfc5/ngff/test_subspace.py": (
        "data_rfc5/ngff/0.6-dev/examples/subspace"
    ),
    "test_data_rfc5/ngff/test_multiscales_strict.py": (
        "data_rfc5/ngff/0.6-dev/examples/multiscales_strict"
    ),
    "test_data_rfc5/ngff/test_coordSystems.py": (
        "data_rfc5/ngff/0.6-dev/examples/coordSystems"
    ),
    # 2d examples
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_2d_axis_dependent.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/2d/axis_dependent"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_2d_basic.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/2d/basic"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_2d_basic_binary.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/2d/basic_binary"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_2d_nonlinear.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/2d/nonlinear"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_2d_simple.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/2d/simple"
    ),
    # 3d examples
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_3d_axis_dependent.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/3d/axis_dependent"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_3d_basic.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/3d/basic"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_3d_basic_binary.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/3d/basic_binary"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_3d_nonlinear.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/3d/nonlinear"
    ),
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_3d_simple.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/3d/simple"
    ),
    # user stories
    "test_data_rfc5/ngff-rfc5-coordinate-transformation-examples/test_user_stories.py": (
        "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2/user_stories"
    ),
}


def get_data_folder(test_file: str) -> str:
    path = Path(test_file)
    rel_path = path.relative_to(path.parents[2])
    for file, folder in TESTS_FILE_TO_DATA_MAPPING.items():
        if rel_path == Path(file):
            return folder
    raise ValueError(f"Test file {test_file} not found in mapping.")


def _parse_data(folder: str, in_memory: T) -> Callable[..., Any]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            test_name = re.sub(r"^test_", "", func.__name__)
            model_cls = type(in_memory)
            file_path_json = get_data_file_path(
                folder=folder, json_fname=f"{test_name}.json"
            )
            file_path_zarr = get_data_file_path(
                folder=folder, json_fname=f"{test_name}.zarr"
            )
            if file_path_json.exists():
                parsed = read_in_json(file_path=file_path_json, model_cls=model_cls)
            elif file_path_zarr.exists():
                parsed = read_in_zarr(file_path=file_path_zarr, model_cls=model_cls)
            else:
                raise FileNotFoundError(
                    f"Neither {file_path_json} nor {file_path_zarr} exists."
                )
            assert parsed == in_memory
            return func(*args, parsed=parsed, **kwargs)

        return inner

    return wrapper


def check_examples_rfc5_are_downloaded() -> None:
    if not (
        Path(__file__).parent
        / "data_rfc5/ngff-rfc5-coordinate-transformation-examples/zarr2"
    ).exists():
        command = "git submodule update --init --recursive"
        raise ValueError(
            "RFC5 full examples are not downloaded. Please consult the README in "
            "`tests/_rfc5_transforms/data_rfc5/README.md` for information on how"
            " to obtain the data."
        )


def _gen_dataset(
    output_coordinate_system: str,
    scale_factors: list[float],
    path: str = "0",
) -> Dataset:
    return Dataset(
        path=path,
        coordinateTransformations=(
            Scale(
                scale=scale_factors,
                input=f"/{path}",
                output=output_coordinate_system,
            ),
        ),
    )


def wrap_coordinate_transformations_and_systems_into_multiscale(
    coordinate_systems: tuple[CoordinateSystem, ...],
    coordinate_transformations: tuple[CoordinateTransformationType, ...],
) -> Multiscale:
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


check_examples_rfc5_are_downloaded()
