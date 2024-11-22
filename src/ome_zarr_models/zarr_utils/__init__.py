from typing import Any, Sequence
from zarr.util import guess_chunks
import numpy as np

def get_path(store: Any) -> str:
    """
    Get a path from a zarr store
    """
    if hasattr(store, "path"):
        return store.path

    return ""


def normalize_chunks(
    chunks: Any,
    shapes: tuple[tuple[int, ...], ...],
    typesizes: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    """
    If chunks is "auto", then use zarr default chunking based on the largest array for all the arrays.
    If chunks is a sequence of ints, then use those chunks for all arrays.
    If chunks is a sequence of sequences of ints, then use those chunks for each array.
    """
    if chunks == "auto":
        # sort shapes by descending size
        params_sorted_descending = sorted(
            zip(shapes, typesizes), key=lambda v: np.prod(v[0]), reverse=True
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