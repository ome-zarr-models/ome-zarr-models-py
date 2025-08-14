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


def normalize_chunks(
    chunks: Any,
    shapes: tuple[tuple[int, ...], ...],
    typesizes: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    """
    If chunks is "auto", then use zarr default chunking based on the
    largest array for all the arrays.
    If chunks is a sequence of ints, then use those chunks for all arrays.
    If chunks is a sequence of sequences of ints, then use those chunks for each array.
    """
    if chunks == "auto":
        # sort shapes by descending size
        params_sorted_descending = sorted(
            zip(shapes, typesizes, strict=False),
            key=lambda v: np.prod(v[0]),  # type: ignore[return-value, arg-type]
            reverse=True,
        )
        return (guess_chunks(*params_sorted_descending[0]),) * len(shapes)
    if isinstance(chunks, Sequence):
        if all(isinstance(element, int) for element in chunks):
            return (tuple(chunks),) * len(shapes)
        if all(isinstance(element, Sequence) for element in chunks):
            if all(all(isinstance(k, int) for k in v) for v in chunks):
                return tuple(map(tuple, chunks))
            else:
                msg = f"Expected a sequence of sequences of ints. Got {chunks} instead."
                raise ValueError(msg)
    msg = f'Input must be a sequence or the string "auto". Got {type(chunks)}'
    raise TypeError(msg)
