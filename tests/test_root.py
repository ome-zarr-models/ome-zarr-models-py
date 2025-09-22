import re
from pathlib import Path

import pytest
import zarr
from zarr.abc.store import Store

import ome_zarr_models.v04
import ome_zarr_models.v05
from ome_zarr_models import open_ome_zarr
from tests.conftest import get_examples_path
from tests.v05.test_image import make_valid_image_group


def test_load_ome_zarr_group() -> None:
    hcs_group = zarr.open_group(
        get_examples_path(version="0.4") / "hcs_example.ome.zarr",
        mode="r",
        zarr_format=2,
    )
    ome_zarr_group = open_ome_zarr(hcs_group)

    assert isinstance(ome_zarr_group, ome_zarr_models.v04.HCS)
    assert ome_zarr_group.ome_zarr_version == "0.4"


def test_load_ome_zarr_group_v05_image_label(store: Store) -> None:
    # Check that images and image-labels are distinguished correctly
    image_group = make_valid_image_group(store)
    ome_zarr_group = open_ome_zarr(image_group)

    assert isinstance(ome_zarr_group, ome_zarr_models.v05.Image)

    # Turn into an image labels by adding the image-label metadata
    attrs = image_group.attrs.asdict()
    attrs["ome"]["image-label"] = {}  # type: ignore[index]
    image_group.update_attributes(attrs)
    ome_zarr_group = open_ome_zarr(image_group)
    assert isinstance(ome_zarr_group, ome_zarr_models.v05.ImageLabel)


def test_load_ome_zarr_group_bad(tmp_path: Path) -> None:
    hcs_group = zarr.create_group(tmp_path / "test")
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            f"Could not successfully validate <Group file://{tmp_path / 'test'}> "
        ),
    ):
        open_ome_zarr(hcs_group)


@pytest.mark.vcr
def test_load_remote_data() -> None:
    grp = open_ome_zarr(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpA_VIP_ASLM_on.zarr",
        version="0.5",
    )
    assert isinstance(grp, ome_zarr_models.v05.Image)
