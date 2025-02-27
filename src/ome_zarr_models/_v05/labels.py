from typing import Any, Self

import numpy as np
import zarr
from pydantic import Field, ValidationError, model_validator

from ome_zarr_models._v05.base import BaseGroupv05, BaseOMEAttrs
from ome_zarr_models._v05.image import Image
from ome_zarr_models.common.validation import check_array_spec, check_group_spec

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
    """
    Check that all multiscales levels of a labels image are valid Label data types.
    """
    for label_path in labels.attributes.ome.labels:
        if label_path not in labels.members:
            raise ValueError(f"Label path '{label_path}' not found in zarr group")
        label_spec = check_group_spec(labels, label_path)
        try:
            image_spec = Image(
                attributes=label_spec.attributes, members=label_spec.members
            )
        except ValidationError as e:
            raise RuntimeError(
                f"Error validating multiscale image at path '{label_path}'. "
                "See above for more detailed error message."
            ) from e

        for multiscale in image_spec.attributes.ome.multiscales:
            for dataset in multiscale.datasets:
                arr_spec = check_array_spec(image_spec, dataset.path)
                dtype = np.dtype(arr_spec.dtype)
                if dtype not in VALID_DTYPES:
                    msg = (
                        "Data type of labels at path "
                        f"'{label_path}/{dataset.path}' is not valid. "
                        f"Got {dtype}, should be one of "
                        f"{[str(x) for x in VALID_DTYPES]}."
                    )
                    raise ValueError(msg)

    return labels


class LabelsAttrs(BaseOMEAttrs):
    """
    Attributes for an OME-Zarr labels dataset.
    """

    labels: list[str] = Field(
        ..., description="List of paths to labels arrays within a labels dataset."
    )


class Labels(
    BaseGroupv05[LabelsAttrs],
):
    """
    An OME-Zarr labels dataset.
    """

    @classmethod
    def from_zarr(cls, group: zarr.Group) -> Self:
        """
        Create an instance of an OME-Zarr image from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr label metadata.
        """
        ret: Self = super().from_zarr(group)

        # Check all labels paths are valid multiscales
        for label_path in ret.attributes.ome.labels:
            try:
                Image.from_zarr(group[label_path])
            except Exception as err:
                msg = (
                    f"Error validating the label path '{label_path}' "
                    "as a OME-Zarr multiscales group."
                )
                raise RuntimeError(msg) from err

        return ret

    _check_valid_dtypes = model_validator(mode="after")(_check_valid_dtypes)
