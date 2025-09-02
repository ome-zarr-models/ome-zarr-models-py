import pytest
from pydantic import ValidationError

from ome_zarr_models._v06.axes import Axis


def test_orientation_only_spatial() -> None:
    with pytest.raises(
        ValidationError, match="Orientation can only be set on a spatial axis"
    ):
        Axis(name="my_axis", type="time", orientation="anterior-to-posterior")
