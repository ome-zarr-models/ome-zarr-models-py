from ome_zarr_models._rfc5_transforms.coordinate_transformations import SpatialMapper
from tests._rfc5_transforms.conftest import read_in_json


def test_identity_transform():
    read_in_json(json_fname="identity.json", model_cls=SpatialMapper)
