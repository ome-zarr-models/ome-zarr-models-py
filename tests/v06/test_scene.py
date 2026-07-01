import pytest

from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v06 import Scene

SCENE_URL = "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/test-data/v0.6.dev3/idr0050/4995115_output_to_ms.zarr/"


# TODO: Update data on remote storage to reflect 0.6.dev4 changes
@pytest.mark.xfail
@pytest.mark.vcr
def test_load_scene() -> None:
    scene = open_ome_zarr(SCENE_URL)
    assert isinstance(scene, Scene)
