import re
from pathlib import Path

import pytest
import zarr

from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v04.hcs import HCS
from tests.conftest import get_examples_path


def test_load_ome_zarr_group() -> None:
    hcs_group = zarr.open_group(
        get_examples_path(version="0.4") / "hcs_example.ome.zarr", mode="r"
    )
    ome_zarr_group = open_ome_zarr(hcs_group)

    assert isinstance(ome_zarr_group, HCS)
    assert ome_zarr_group.ome_zarr_version == "0.4"


def test_load_ome_zarr_group_bad(tmp_path: Path) -> None:
    hcs_group = zarr.create_group(tmp_path / "test")
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            f"Could not successfully validate <Group file://{tmp_path / 'test'}> "
        ),
    ):
        open_ome_zarr(hcs_group)
