import pytest

from tests._v06.conftest import get_data_folder

FOLDER = get_data_folder(__file__)


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
