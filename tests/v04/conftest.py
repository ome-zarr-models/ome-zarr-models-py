import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, TypeVar

import numcodecs
import numpy as np
import numpy.typing as npt
import zarr
import zarr.storage
from numcodecs.abc import Codec
from pydantic_zarr.v2 import ArraySpec, GroupSpec
from zarr.core.chunk_grids import _guess_chunks as guess_chunks

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.image import Image, ImageAttrs
from ome_zarr_models.v04.multiscales import (
    Dataset,
    Multiscale,
)

T = TypeVar("T", bound=BaseAttrs)


def read_in_json(*, json_fname: str, model_cls: type[T]) -> T:
    """
    Read a JSON file into a ome-zarr-models base attributes class.
    """
    with open(Path(__file__).parent / "data" / json_fname) as f:
        return model_cls.model_validate_json(f.read())


def json_to_zarr_group(*, json_fname: str) -> zarr.Group:
    """
    Create an empty Zarr group, and set the attributes from a JSON file.
    """
    group = zarr.open_group(store=zarr.storage.MemoryStore(), zarr_format=2)
    with open(Path(__file__).parent / "data" / json_fname) as f:
        attrs = json.load(f)

    group.attrs.put(attrs)
    return group
