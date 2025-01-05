from pathlib import Path

import zarr

from ome_zarr_models import load_ome_zarr_group
from ome_zarr_models.v04.hcs import HCS


def test_load_ome_zarr_group() -> None:
    hcs_group = zarr.open(
        Path(__file__).parent / "v04" / "data" / "hcs_example.ome.zarr", mode="r"
    )
    ome_zarr_group = load_ome_zarr_group(hcs_group)

    assert isinstance(ome_zarr_group, HCS)
    assert ome_zarr_group.ome_zarr_version == "0.4"
