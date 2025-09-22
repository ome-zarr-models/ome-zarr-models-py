from typing import Self

from pydantic import JsonValue, model_validator

from ome_zarr_models._v06.axes import Axes
from ome_zarr_models.common.multiscales import Dataset, MultiscaleBase

__all__ = ["Dataset", "Multiscale"]


class Multiscale(MultiscaleBase):
    """
    An element of multiscales metadata.
    """

    axes: Axes

    @model_validator(mode="after")
    def _ensure_valid_orientations(self: Self) -> Self:
        """
        Validate anatomical orientations.
        """
        orientations: list[JsonValue] = [
            a.orientation.value for a in self.axes if a.orientation is not None
        ]
        _check_only_one_value(
            orientations=orientations, values=["right-to-left", "left-to-right"]
        )
        _check_only_one_value(
            orientations=orientations,
            values=["anterior-to-posterior", "posterior-to-anterior"],
        )
        _check_only_one_value(
            orientations=orientations,
            values=[
                "inferior-to-superior",
                "superior-to-inferior",
                "dorsal-to-ventral",
                "ventral-to-dorsal",
                "dorsal-to-palmar",
                "palmar-to-dorsal",
                "dorsal-to-plantar",
                "plantar-to-dorsal",
                "rostral-to-caudal",
                "caudal-to-rostral",
                "cranial-to-caudal",
                "caudal-to-cranial",
                "proximal-to-distal",
                "distal-to-proximal",
            ],
        )
        return self


def _check_only_one_value(
    *, orientations: list[JsonValue], values: list[JsonValue]
) -> None:
    counter = 0
    for value in values:
        if value in orientations:
            counter += 1

    if counter > 1:
        raise ValueError(f"Only one of {values} allowed in a set of axes.")
