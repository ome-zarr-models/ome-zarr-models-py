"""
Test loading data from IDR.
"""

from contextlib import AbstractContextManager, nullcontext
from typing import Any

import pytest
import zarr

import ome_zarr_models.v05
from ome_zarr_models.exceptions import ValidationWarning


@pytest.mark.vcr
@pytest.mark.parametrize(
    ("url", "cls", "expected_warning"),
    [
        (
            "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpA_VIP_ASLM_on.zarr",
            ome_zarr_models.v05.Image,
            None,
        ),
        (
            "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
            ome_zarr_models.v05.Image,
            None,
        ),
        # See https://github.com/IDR/ome-ngff-samples/issues/30
        # (
        #    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0062A/6001240_labels.zarr",
        #    ome_zarr_models.v05.Image,
        #    None,
        # ),
        (
            "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0157/"
            "Asterella gracilis SWE/"
            "IMG_1033-1112 Asterella gracilis (Mannia gracilis) stature.ome.zarr",
            ome_zarr_models.v05.Image,
            None,
        ),
        (
            "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0033A/BR00109990_C2.zarr",
            ome_zarr_models.v05.BioFormats2Raw,
            None,
        ),
        # The next dataset takes a long time (> 10 mins) to open, so comment out for now
        # ("https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0010/76-45.ome.zarr",
        # ome_zarr_models.v05.HCS,
        # re.escape("'version' field not specified in plate metadata"))
        (
            "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0076A/10501752.zarr",
            ome_zarr_models.v04.Image,
            None,
        ),
    ],
)
def test_load_remote_data(
    url: str,
    cls: type[ome_zarr_models.v05.base.BaseGroupv05[Any]],
    expected_warning: str | None,
) -> None:
    ctx: AbstractContextManager[Any]
    if expected_warning is not None:
        ctx = pytest.warns(ValidationWarning, match=expected_warning)
    else:
        ctx = nullcontext()

    with ctx:
        grp = cls.from_zarr(zarr.open_group(url))
    assert isinstance(grp, cls)
