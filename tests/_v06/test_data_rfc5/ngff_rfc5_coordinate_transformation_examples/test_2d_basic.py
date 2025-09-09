import pytest

from tests._v06.conftest import get_data_folder_for_current_tests_file

FOLDER = get_data_folder_for_current_tests_file(__file__)


@pytest.mark.skip
def test_identity() -> None:
    pass


@pytest.mark.skip
def test_scale() -> None:
    pass


@pytest.mark.skip
def test_scale_multiscale() -> None:
    pass


@pytest.mark.skip
def test_sequenceScaleTranslation() -> None:
    pass


@pytest.mark.skip
def test_sequenceScaleTranslation_multiscale() -> None:
    pass


@pytest.mark.skip
def test_translation() -> None:
    pass
