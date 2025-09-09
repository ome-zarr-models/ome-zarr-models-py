import pytest

from tests._v06.conftest import get_data_folder_for_current_tests_file

FOLDER = get_data_folder_for_current_tests_file(__file__)


@pytest.mark.skip
def test_subspaceMultidim() -> None:
    pass


@pytest.mark.skip
def test_subspacePermute() -> None:
    pass
