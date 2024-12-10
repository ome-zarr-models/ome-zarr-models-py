from pathlib import Path

import zarr

from ome_zarr_models.v04 import HCS


def test_example_hcs() -> None:
    group = zarr.open(Path(__file__).parent / "data" / "hcs_example.ome.zarr", mode="r")
    hcs = HCS.from_zarr(group)
    assert hcs.attributes == None
