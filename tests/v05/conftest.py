import json
from pathlib import Path
from typing import TypeVar

import zarr
import zarr.storage

from ome_zarr_models.base import BaseAttrs

T = TypeVar("T", bound=BaseAttrs)


def read_in_json(*, json_fname: str, model_cls: type[T]) -> T:
    """
    Read a JSON file into a ome-zarr-models base attributes class.
    """
    with open(Path(__file__).parent / "data" / json_fname) as f:
        return model_cls.model_validate_json(f.read())


def json_to_zarr_group(*, json_fname: str) -> zarr.Group:
    """
    Create an empty Zarr group, and set attributes from a JSON file.
    """
    group = zarr.open_group(store=zarr.storage.MemoryStore(), zarr_format=3)
    with open(Path(__file__).parent / "data" / json_fname) as f:
        attrs = json.load(f)

    group.attrs.put(attrs)
    return group
