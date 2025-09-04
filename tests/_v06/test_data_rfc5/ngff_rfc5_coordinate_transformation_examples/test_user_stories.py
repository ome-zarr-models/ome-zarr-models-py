import pytest

from tests._v06.conftest import get_data_folder_for_current_tests_file

FOLDER = get_data_folder_for_current_tests_file(__file__)


@pytest.mark.skip
def test_image_registration_3d() -> None:
    pass


@pytest.mark.skip
def test_lens_correction() -> None:
    pass


@pytest.mark.skip
def test_stitched_tiles_2d() -> None:
    pass


@pytest.mark.skip
def test_stitched_tiles_3d() -> None:
    pass
