from pathlib import Path

import pytest
import zarr
import zarr.errors

from ome_zarr_models._v06.image import Image

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
    if zarr_path_relative in [
        Path("2d/basic_binary/translationParams.zarr"),
        Path("2d/simple/affineParams.zarr"),
        Path("2d/simple/rotationParams.zarr"),
        Path("3d/axis_dependent/mapAxis.zarr"),
        Path("3d/simple/affineParams.zarr"),
        Path("user_stories/SCAPE.zarr"),
        Path("user_stories/image_registration_3d.zarr"),
        Path("user_stories/lens_correction.zarr"),
        Path("user_stories/stitched_tiles_2d.zarr"),
        Path("user_stories/stitched_tiles_3d.zarr"),
    ]:
        pytest.xfail("Example currently failing")
    elif "byDimension" in str(zarr_path):
        pytest.xfail("byDimension not correctly implemented")

    zarr_group = zarr.open_group(zarr_path, mode="r")
    try:
        Image.from_zarr(zarr_group)
    except NotImplementedError as e:
        if "from a Zarr array not yet implemented" in str(e):
            pytest.xfail(
                "Loading transformation parameters from a Zarr array not yet supported"
            )
        raise


def test_get_all_zarrs() -> None:
    zarrs = get_all_zarrs(TEST_DATA_PATH)
    assert len([z.relative_to(TEST_DATA_PATH) for z in zarrs]) == 38
