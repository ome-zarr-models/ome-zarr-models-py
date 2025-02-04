from typing import Any

import numpy as np
from pydantic import Field, model_validator
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs, BaseZarrAttrs

__all__ = ["Labels", "LabelsAttrs"]


VALID_DTYPES: list[np.dtype[Any]] = [
    np.dtype(x)
    for x in [
        np.uint8,
        np.int8,
        np.uint16,
        np.int16,
        np.uint32,
        np.int32,
        np.uint64,
        np.int64,
    ]
]


def _check_valid_dtypes(labels: "Labels") -> "Labels":
    for label_path in labels.attributes.ome.labels:
        if label_path not in labels.members:
            raise ValueError(f"Label path '{label_path}' not found in zarr group")
        else:
            spec = labels.members[label_path]
            if isinstance(spec, GroupSpec):
                raise ValueError(
                    f"Label path '{label_path}' points to a group, not an array"
                )

            dtype = np.dtype(spec.dtype)
            if dtype not in VALID_DTYPES:
                raise ValueError(
                    f"Data type of labels at '{label_path}' is not valid. "
                    f"Got {dtype}, should be one of {[str(x) for x in VALID_DTYPES]}."
                )

    return labels


class LabelsAttrs(BaseOMEAttrs):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class Labels(
    GroupSpec[BaseZarrAttrs[LabelsAttrs], ArraySpec | GroupSpec],  # type: ignore[misc]
    BaseGroupv05,
):
    """
    An OME-Zarr labels dataset.
    """

    _check_valid_dtypes = model_validator(mode="after")(_check_valid_dtypes)
