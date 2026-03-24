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

image_group_v06 = ome_zarr_models._v06.Image.from_v05(image_group_v05)
print(image_group_v06.ome_attributes)
