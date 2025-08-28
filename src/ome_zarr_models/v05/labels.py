from typing import Any, Self

import numpy as np
import zarr
import zarr.errors
from pydantic import Field, ValidationError, model_validator
from pydantic_zarr.v3 import AnyArraySpec, AnyGroupSpec, GroupSpec

from ome_zarr_models.common.validation import check_array_spec, check_group_spec
from ome_zarr_models.v05.base import BaseGroupv05, BaseOMEAttrs

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
    from ome_zarr_models.v05.image import Image

    if labels.members is None:
        raise RuntimeError(f"{labels.members=}")

    for label_path in labels.attributes.ome.labels:
        if label_path not in labels.members:
            raise ValueError(f"Label path '{label_path}' not found in zarr group")
        label_spec = check_group_spec(labels, label_path)  # type: ignore[arg-type]
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
                arr_spec = check_array_spec(image_spec, dataset.path)  # type: ignore[arg-type]
                if (
                    not isinstance(arr_spec.data_type, str)
                    or np.dtype(arr_spec.data_type) not in VALID_DTYPES
                ):
                    msg = (
                        "Data type of labels at path "
                        f"'{label_path}/{dataset.path}' is not valid. "
                        f"Got {arr_spec.data_type}, should be one of "
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
    def from_zarr(cls, group: zarr.Group) -> Self:  # type: ignore[override]
        """
        Create an OME-Zarr labels model from a `zarr.Group`.

        Parameters
        ----------
        group : zarr.Group
            A Zarr group that has valid OME-Zarr label metadata.
        """
        from ome_zarr_models.v05.image import Image

        attrs_dict = group.attrs.asdict()
        label_attrs = LabelsAttrs.model_validate(group.attrs.asdict()["ome"])

        # Extract Zarr Image paths from multiscale metadata
        members_tree_flat: dict[str, AnyGroupSpec | AnyArraySpec] = {}
        for label_path in label_attrs.labels:
            try:
                image_group = zarr.open_group(
                    store=group.store, path=label_path, mode="r"
                )
                image_model = Image.from_zarr(image_group).to_flat()
                for path in image_model:
                    members_tree_flat["/" + label_path + path] = image_model[path]
            except zarr.errors.GroupNotFoundError as err:
                raise ValueError(
                    f"Label path '{label_path}' not found in zarr group"
                ) from err
            except Exception as err:
                msg = (
                    f"Error validating the label path '{label_path}' "
                    "as a OME-Zarr multiscales group."
                )
                raise RuntimeError(msg) from err

        members_normalized: AnyGroupSpec = GroupSpec.from_flat(members_tree_flat)
        return cls(attributes=attrs_dict, members=members_normalized.members)

    _check_valid_dtypes = model_validator(mode="after")(_check_valid_dtypes)
