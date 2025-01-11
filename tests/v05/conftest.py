import json
from pathlib import Path
from typing import TypeVar

import zarr

from ome_zarr_models.base import BaseAttrs

T = TypeVar("T", bound=BaseAttrs)


def json_to_zarr_group(*, json_fname: str) -> zarr.Group:
    """
    Create an empty Zarr group, and set attributes from a JSON file.
    """
    group = zarr.open_group(store=zarr.MemoryStore())
    with open(Path(__file__).parent / "data" / json_fname) as f:
        attrs = json.load(f)

    group.attrs.put(attrs)
    return group
