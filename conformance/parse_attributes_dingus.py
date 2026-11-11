#!/usr/bin/env python3
"""A dingus for oztest parse_attributes conformance testing.

https://github.com/German-BioImaging/oztest/tree/main/cases/parse_attributes

To run, install oztest (https://github.com/German-BioImaging/oztest). Then run:
    oztest run parse_attributes ./scripts/parse_attributes_dingus.py
"""

import json
import sys

from pydantic import ValidationError

from ome_zarr_models import validate_ome_zarr_json

attrs = json.load(open(sys.argv[1]))

try:
    ome_zarr_attrs = validate_ome_zarr_json(attrs)
    d = {"validity": "valid", "message": f"Got {type(ome_zarr_attrs)}"}
except ValidationError as e:
    d = {"validity": "invalid", "message": str(e)}

print(json.dumps(d))
