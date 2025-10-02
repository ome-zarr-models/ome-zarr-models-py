from pathlib import Path

import pytest
import zarr

from ome_zarr_models._v06.image import Image

from .expected_attributes import expected_attrs

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

    return zarrs


# List of paths to examples that are currently failing.
# TODO: remove these one by one and fix
failing_zarrs = [
    Path("3d/axis_dependent/byDimension.zarr"),
    Path("3d/axis_dependent/mapAxis.zarr"),
    Path("3d/basic/scale.zarr"),
    Path("3d/basic/sequenceScaleTranslation.zarr"),
    Path("3d/basic/sequenceScaleTranslation_multiscale.zarr"),
    Path("3d/basic/scale_multiscale.zarr"),
    Path("3d/basic/identity.zarr"),
    Path("3d/basic/translation.zarr"),
    Path("3d/simple/affine.zarr"),
    Path("3d/simple/rotationParams.zarr"),
    Path("3d/simple/rotation.zarr"),
    Path("3d/simple/affine_multiscale.zarr"),
    Path("3d/simple/affineParams.zarr"),
    Path("3d/basic_binary/scaleParams.zarr"),
    Path("3d/basic_binary/translationParams.zarr"),
    Path("3d/nonlinear/invDisplacements.zarr"),
    Path("3d/nonlinear/invCoordinates.zarr"),
    Path("zarr2/3d/axis_dependent/byDimension.zarr"),
    Path("zarr2/3d/axis_dependent/mapAxis.zarr"),
    Path("zarr2/3d/basic/scale.zarr"),
    Path("zarr2/3d/basic/sequenceScaleTranslation.zarr"),
    Path("zarr2/3d/basic/sequenceScaleTranslation_multiscale.zarr"),
    Path("zarr2/3d/basic/scale_multiscale.zarr"),
    Path("zarr2/3d/basic/identity.zarr"),
    Path("zarr2/3d/basic/translation.zarr"),
    Path("zarr2/3d/simple/affine.zarr"),
    Path("zarr2/3d/simple/rotationParams.zarr"),
    Path("zarr2/3d/simple/rotation.zarr"),
    Path("zarr2/3d/simple/affine_multiscale.zarr"),
    Path("zarr2/3d/simple/affineParams.zarr"),
    Path("zarr2/3d/basic_binary/scaleParams.zarr"),
    Path("zarr2/3d/basic_binary/translationParams.zarr"),
    Path("zarr2/3d/nonlinear/invDisplacements.zarr"),
    Path("zarr2/3d/nonlinear/invCoordinates.zarr"),
    Path("zarr2/2d/axis_dependent/byDimension.zarr"),
    Path("zarr2/2d/axis_dependent/mapAxis.zarr"),
    Path("zarr2/2d/basic/scale.zarr"),
    Path("zarr2/2d/basic/sequenceScaleTranslation.zarr"),
    Path("zarr2/2d/basic/sequenceScaleTranslation_multiscale.zarr"),
    Path("zarr2/2d/basic/scale_multiscale.zarr"),
    Path("zarr2/2d/basic/identity.zarr"),
    Path("zarr2/2d/basic/translation.zarr"),
    Path("zarr2/2d/simple/affine.zarr"),
    Path("zarr2/2d/simple/rotationParams.zarr"),
    Path("zarr2/2d/simple/rotation.zarr"),
    Path("zarr2/2d/simple/affine_multiscale.zarr"),
    Path("zarr2/2d/simple/affineParams.zarr"),
    Path("zarr2/2d/basic_binary/scaleParams.zarr"),
    Path("zarr2/2d/basic_binary/translationParams.zarr"),
    Path("zarr2/2d/nonlinear/invDisplacements.zarr"),
    Path("zarr2/2d/nonlinear/invCoordinates.zarr"),
    Path("zarr2/user_stories/stitched_tiles_3d.zarr"),
    Path("zarr2/user_stories/stitched_tiles_2d.zarr"),
    Path("zarr2/user_stories/image_registration_3d.zarr"),
    Path("zarr2/user_stories/lens_correction.zarr"),
    Path("2d/axis_dependent/byDimension.zarr"),
    Path("2d/axis_dependent/mapAxis.zarr"),
    Path("2d/basic/scale.zarr"),
    Path("2d/basic/sequenceScaleTranslation.zarr"),
    Path("2d/basic/sequenceScaleTranslation_multiscale.zarr"),
    Path("2d/basic/scale_multiscale.zarr"),
    Path("2d/basic/identity.zarr"),
    Path("2d/basic/translation.zarr"),
    Path("2d/simple/affine.zarr"),
    Path("2d/simple/rotationParams.zarr"),
    Path("2d/simple/rotation.zarr"),
    Path("2d/simple/affine_multiscale.zarr"),
    Path("2d/simple/affineParams.zarr"),
    Path("2d/basic_binary/scaleParams.zarr"),
    Path("2d/basic_binary/translationParams.zarr"),
    Path("2d/nonlinear/invDisplacements.zarr"),
    Path("2d/nonlinear/invCoordinates.zarr"),
    Path("user_stories/stitched_tiles_3d.zarr"),
    Path("user_stories/stitched_tiles_2d.zarr"),
    Path("user_stories/image_registration_3d.zarr"),
    Path("user_stories/lens_correction.zarr"),
]


@pytest.mark.parametrize("zarr_path", get_all_zarrs(TEST_DATA_PATH))
def test_basic(zarr_path: Path) -> None:
    if zarr_path.relative_to(TEST_DATA_PATH) in failing_zarrs:
        pytest.xfail()

    zarr_group = zarr.open_group(zarr_path, mode="r")
    ome_group = Image.from_zarr(zarr_group)

    if expected_attrs[zarr_path] is None:
        print(f"Expected attributes not set in expected_attributes.py for {zarr_path}")
    assert ome_group.ome_attributes == expected_attrs[zarr_path]


def test_get_all_zarrs() -> None:
    zarrs = get_all_zarrs(TEST_DATA_PATH)
    assert [z.relative_to(TEST_DATA_PATH) for z in zarrs] == [
        Path("3d/axis_dependent/byDimension.zarr"),
        Path("3d/axis_dependent/mapAxis.zarr"),
        Path("3d/basic/scale.zarr"),
        Path("3d/basic/sequenceScaleTranslation.zarr"),
        Path("3d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("3d/basic/scale_multiscale.zarr"),
        Path("3d/basic/identity.zarr"),
        Path("3d/basic/translation.zarr"),
        Path("3d/simple/affine.zarr"),
        Path("3d/simple/rotationParams.zarr"),
        Path("3d/simple/rotation.zarr"),
        Path("3d/simple/affine_multiscale.zarr"),
        Path("3d/simple/affineParams.zarr"),
        Path("3d/basic_binary/scaleParams.zarr"),
        Path("3d/basic_binary/translationParams.zarr"),
        Path("3d/nonlinear/invDisplacements.zarr"),
        Path("3d/nonlinear/invCoordinates.zarr"),
        Path("zarr2/3d/axis_dependent/byDimension.zarr"),
        Path("zarr2/3d/axis_dependent/mapAxis.zarr"),
        Path("zarr2/3d/basic/scale.zarr"),
        Path("zarr2/3d/basic/sequenceScaleTranslation.zarr"),
        Path("zarr2/3d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("zarr2/3d/basic/scale_multiscale.zarr"),
        Path("zarr2/3d/basic/identity.zarr"),
        Path("zarr2/3d/basic/translation.zarr"),
        Path("zarr2/3d/simple/affine.zarr"),
        Path("zarr2/3d/simple/rotationParams.zarr"),
        Path("zarr2/3d/simple/rotation.zarr"),
        Path("zarr2/3d/simple/affine_multiscale.zarr"),
        Path("zarr2/3d/simple/affineParams.zarr"),
        Path("zarr2/3d/basic_binary/scaleParams.zarr"),
        Path("zarr2/3d/basic_binary/translationParams.zarr"),
        Path("zarr2/3d/nonlinear/invDisplacements.zarr"),
        Path("zarr2/3d/nonlinear/invCoordinates.zarr"),
        Path("zarr2/2d/axis_dependent/byDimension.zarr"),
        Path("zarr2/2d/axis_dependent/mapAxis.zarr"),
        Path("zarr2/2d/basic/scale.zarr"),
        Path("zarr2/2d/basic/sequenceScaleTranslation.zarr"),
        Path("zarr2/2d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("zarr2/2d/basic/scale_multiscale.zarr"),
        Path("zarr2/2d/basic/identity.zarr"),
        Path("zarr2/2d/basic/translation.zarr"),
        Path("zarr2/2d/simple/affine.zarr"),
        Path("zarr2/2d/simple/rotationParams.zarr"),
        Path("zarr2/2d/simple/rotation.zarr"),
        Path("zarr2/2d/simple/affine_multiscale.zarr"),
        Path("zarr2/2d/simple/affineParams.zarr"),
        Path("zarr2/2d/basic_binary/scaleParams.zarr"),
        Path("zarr2/2d/basic_binary/translationParams.zarr"),
        Path("zarr2/2d/nonlinear/invDisplacements.zarr"),
        Path("zarr2/2d/nonlinear/invCoordinates.zarr"),
        Path("zarr2/user_stories/stitched_tiles_3d.zarr"),
        Path("zarr2/user_stories/stitched_tiles_2d.zarr"),
        Path("zarr2/user_stories/image_registration_3d.zarr"),
        Path("zarr2/user_stories/lens_correction.zarr"),
        Path("2d/axis_dependent/byDimension.zarr"),
        Path("2d/axis_dependent/mapAxis.zarr"),
        Path("2d/basic/scale.zarr"),
        Path("2d/basic/sequenceScaleTranslation.zarr"),
        Path("2d/basic/sequenceScaleTranslation_multiscale.zarr"),
        Path("2d/basic/scale_multiscale.zarr"),
        Path("2d/basic/identity.zarr"),
        Path("2d/basic/translation.zarr"),
        Path("2d/simple/affine.zarr"),
        Path("2d/simple/rotationParams.zarr"),
        Path("2d/simple/rotation.zarr"),
        Path("2d/simple/affine_multiscale.zarr"),
        Path("2d/simple/affineParams.zarr"),
        Path("2d/basic_binary/scaleParams.zarr"),
        Path("2d/basic_binary/translationParams.zarr"),
        Path("2d/nonlinear/invDisplacements.zarr"),
        Path("2d/nonlinear/invCoordinates.zarr"),
        Path("user_stories/stitched_tiles_3d.zarr"),
        Path("user_stories/stitched_tiles_2d.zarr"),
        Path("user_stories/image_registration_3d.zarr"),
        Path("user_stories/lens_correction.zarr"),
    ]
