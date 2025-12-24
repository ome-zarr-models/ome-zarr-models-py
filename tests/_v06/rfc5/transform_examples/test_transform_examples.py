from pathlib import Path

import pytest
import zarr
import zarr.errors

from ome_zarr_models._v06.image import Image
from ome_zarr_models._v06.scene import Scene

TEST_DATA_PATH = Path(__file__).parent / "ngff-rfc5-coordinate-transformation-examples"


def get_all_zarrs(directory: Path) -> list[Path]:
    zarrs: list[Path] = []
    for f in directory.glob("*"):
        if f.is_dir():
            if f.suffix == ".zarr":
                # Found a Zarr group
                zarrs.append(f)
            else:
                # Recurse
                zarrs += get_all_zarrs(f)

    return sorted(zarrs)


@pytest.mark.parametrize(
    "zarr_path",
    get_all_zarrs(TEST_DATA_PATH),
    ids=[str(p.relative_to(TEST_DATA_PATH)) for p in get_all_zarrs(TEST_DATA_PATH)],
)
def test_basic(zarr_path: Path) -> None:
    """
    Test loading OME-Zarr datasets with transforms.

    Currently this just smoke tests that they load,
    and not that the values are as expected.
    """
    print(zarr_path)
    zarr_path_relative = zarr_path.relative_to(TEST_DATA_PATH)
    # These have broken metadata; once metadata is fixed, re-enable tests
    if "byDimension" in str(zarr_path):
        pytest.xfail("byDimension not correctly implemented")
    if "inv" in str(zarr_path):
        pytest.xfail("Inverse transforms no longer supported")

    cls = Scene if zarr_path_relative.parts[0] == "user_stories" else Image
    zarr_group = zarr.open_group(zarr_path, mode="r")
    try:
        cls.from_zarr(zarr_group)
    except NotImplementedError as e:
        if "from a Zarr array not yet implemented" in str(e):
            pytest.xfail(
                "Loading transformation parameters from a Zarr array not yet supported"
            )
        raise


def test_get_all_zarrs() -> None:
    zarrs = get_all_zarrs(TEST_DATA_PATH)
    assert len([z.relative_to(TEST_DATA_PATH) for z in zarrs]) == 39
