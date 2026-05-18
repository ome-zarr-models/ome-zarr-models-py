# This page explains how to convert metadata from one OME-Zarr version to another.
#
# ## 0.5 to 0.6
#
# The main addition to OME-Zarr in version 0.6 is coordinate systems.


import zarr.storage
from rich import print

import ome_zarr_models._v06
import ome_zarr_models.v05

zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
image_group_v05 = ome_zarr_models.v05.Image.from_zarr(zarr_group)
print(image_group_v05.ome_attributes)

# ## Metadata conversion
#
# ome-zarr-models-py offers a convenient way to convert multiscales metadata
# between different ome-zarr versions without using the high-level
# `Image` classes:

multiscale = ome_zarr_models.v05.multiscales.Multiscale.model_validate(
    {
        "axes": [
            {"name": "z", "type": "space"},
            {"name": "y", "type": "space"},
            {"name": "x", "type": "space"},
        ],
        "datasets": [  # an image with a single resolution level
            {
                "path": "s0",
                "coordinateTransformations": [
                    {
                        "type": "scale",
                        "scale": [1, 1, 1],
                    }
                ],
            }
        ],
        "name": "my_image",
    }
)

multiscale_v06 = multiscale.to_version("0.6")
print(multiscale_v06)

# This version conversion works between all currently supported versions of ome-zarr:

multiscale_v04 = multiscale.to_version("0.4")
print(multiscale_v04)
