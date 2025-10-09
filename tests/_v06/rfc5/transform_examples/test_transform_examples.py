from pathlib import Path

import pytest
import zarr

from ome_zarr_models._v06.image import Image

TEST_DATA_PATH = Path(__file__).parent / "ngff-rfc5-coordinate-transformation-examples"
FAILING_PATHS_FILE = Path(__file__).parent / "failing_zarrs.txt"


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


# List of paths to examples that are currently failing.
with open(FAILING_PATHS_FILE) as f:
    failing_zarrs = {Path(line.removesuffix("\n")) for line in f.readlines()}


# Function to rewrite the list of failing exmaples
def write_failing_zarrs(failing_zarrs: set[Path]) -> None:
    with open(FAILING_PATHS_FILE, "w") as f:
        for line in sorted(failing_zarrs):
            f.write(f"{line}\n")


@pytest.mark.parametrize("zarr_path", get_all_zarrs(TEST_DATA_PATH))
def test_basic(zarr_path: Path) -> None:
    """
    Test loading OME-Zarr datasets with transforms.

    Currently this just smoke tests that they load,
    and not that the values are as expected.
    """
    print(zarr_path)
    zarr_path_relative = zarr_path.relative_to(TEST_DATA_PATH)

    try:
        zarr_group = zarr.open_group(zarr_path, mode="r")
        Image.from_zarr(zarr_group)
    except Exception as e:
        if zarr_path_relative in failing_zarrs:
            raise e
        else:
            # Failed but not already in list of failing files;
            # add to list of failing files
            failing_zarrs.add(zarr_path_relative)
            write_failing_zarrs(failing_zarrs)
            raise e

    # Succeeded; remove from list of failing files
    if zarr_path_relative in failing_zarrs:
        failing_zarrs.remove(zarr_path_relative)
        write_failing_zarrs(failing_zarrs)
        raise RuntimeError(
            "List of failing zarr paths not up to date. "
            "List has been updated, please commit the change."
        )


def test_get_all_zarrs() -> None:
    zarrs = get_all_zarrs(TEST_DATA_PATH)
    assert [z.relative_to(TEST_DATA_PATH) for z in zarrs] == [
        Path("2d/axis_dependent/byDimension.zarr"),
        Path("2d/axis_dependent/mapAxis.zarr"),
        Path("2d/basic/identity.zarr"),
        Path("2d/basic/scale.zarr"),
        Path("2d/basic/scale_multiscale.zarr"),
        Path("2d/basic/sequenceScaleTranslation.zarr"),
        Path("2d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("2d/basic/translation.zarr"),
        Path("2d/basic_binary/scaleParams.zarr"),
        Path("2d/basic_binary/translationParams.zarr"),
        Path("2d/nonlinear/invCoordinates.zarr"),
        Path("2d/nonlinear/invDisplacements.zarr"),
        Path("2d/simple/affine.zarr"),
        Path("2d/simple/affineParams.zarr"),
        Path("2d/simple/affine_multiscale.zarr"),
        Path("2d/simple/rotation.zarr"),
        Path("2d/simple/rotationParams.zarr"),
        Path("3d/axis_dependent/byDimension.zarr"),
        Path("3d/axis_dependent/mapAxis.zarr"),
        Path("3d/basic/identity.zarr"),
        Path("3d/basic/scale.zarr"),
        Path("3d/basic/scale_multiscale.zarr"),
        Path("3d/basic/sequenceScaleTranslation.zarr"),
        Path("3d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("3d/basic/translation.zarr"),
        Path("3d/basic_binary/scaleParams.zarr"),
        Path("3d/basic_binary/translationParams.zarr"),
        Path("3d/nonlinear/invCoordinates.zarr"),
        Path("3d/nonlinear/invDisplacements.zarr"),
        Path("3d/simple/affine.zarr"),
        Path("3d/simple/affineParams.zarr"),
        Path("3d/simple/affine_multiscale.zarr"),
        Path("3d/simple/rotation.zarr"),
        Path("3d/simple/rotationParams.zarr"),
        Path("user_stories/image_registration_3d.zarr"),
        Path("user_stories/lens_correction.zarr"),
        Path("user_stories/stitched_tiles_2d.zarr"),
        Path("user_stories/stitched_tiles_3d.zarr"),
        Path("zarr2/2d/axis_dependent/byDimension.zarr"),
        Path("zarr2/2d/axis_dependent/mapAxis.zarr"),
        Path("zarr2/2d/basic/identity.zarr"),
        Path("zarr2/2d/basic/scale.zarr"),
        Path("zarr2/2d/basic/scale_multiscale.zarr"),
        Path("zarr2/2d/basic/sequenceScaleTranslation.zarr"),
        Path("zarr2/2d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("zarr2/2d/basic/translation.zarr"),
        Path("zarr2/2d/basic_binary/scaleParams.zarr"),
        Path("zarr2/2d/basic_binary/translationParams.zarr"),
        Path("zarr2/2d/nonlinear/invCoordinates.zarr"),
        Path("zarr2/2d/nonlinear/invDisplacements.zarr"),
        Path("zarr2/2d/simple/affine.zarr"),
        Path("zarr2/2d/simple/affineParams.zarr"),
        Path("zarr2/2d/simple/affine_multiscale.zarr"),
        Path("zarr2/2d/simple/rotation.zarr"),
        Path("zarr2/2d/simple/rotationParams.zarr"),
        Path("zarr2/3d/axis_dependent/byDimension.zarr"),
        Path("zarr2/3d/axis_dependent/mapAxis.zarr"),
        Path("zarr2/3d/basic/identity.zarr"),
        Path("zarr2/3d/basic/scale.zarr"),
        Path("zarr2/3d/basic/scale_multiscale.zarr"),
        Path("zarr2/3d/basic/sequenceScaleTranslation.zarr"),
        Path("zarr2/3d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("zarr2/3d/basic/translation.zarr"),
        Path("zarr2/3d/basic_binary/scaleParams.zarr"),
        Path("zarr2/3d/basic_binary/translationParams.zarr"),
        Path("zarr2/3d/nonlinear/invCoordinates.zarr"),
        Path("zarr2/3d/nonlinear/invDisplacements.zarr"),
        Path("zarr2/3d/simple/affine.zarr"),
        Path("zarr2/3d/simple/affineParams.zarr"),
        Path("zarr2/3d/simple/affine_multiscale.zarr"),
        Path("zarr2/3d/simple/rotation.zarr"),
        Path("zarr2/3d/simple/rotationParams.zarr"),
        Path("zarr2/user_stories/image_registration_3d.zarr"),
        Path("zarr2/user_stories/lens_correction.zarr"),
        Path("zarr2/user_stories/stitched_tiles_2d.zarr"),
        Path("zarr2/user_stories/stitched_tiles_3d.zarr"),
    ]
