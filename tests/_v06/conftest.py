from functools import partial
from typing import Literal

from tests import conftest

VERSION: Literal["0.6"] = "0.6"
json_to_dict = partial(conftest.json_to_dict, version=VERSION)
read_in_json = partial(conftest.read_in_json, version=VERSION)
json_to_zarr_group = partial(conftest.json_to_zarr_group, version=VERSION)
