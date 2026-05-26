# This page explains how to convert metadata from one OME-Zarr version to another.
#
# ## 0.5 to 0.6
#
# The main addition to OME-Zarr in version 0.6 is coordinate systems for images.


import zarr.storage
from rich import print

import ome_zarr_models.v05
import ome_zarr_models.v06

zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
image_group_v05 = ome_zarr_models.v05.Image.from_zarr(zarr_group)
image_attributes_v05 = image_group_v05.ome_attributes
print(image_attributes_v05)

image_attributes_v06 = image_attributes_v05.to_version(
    "0.6", default_cs_name="intrinsic"
)
print(image_attributes_v06)

# The 0.6 specification provides some new fields over the 0.5 version,
# such as the `coordinateSystems` field,
# which provides named coordinate system references.
#
# In the process of conversion, these new fields are provided with default values
# (i.e., the `name` of the default coordinate system is set to "physical").
# However, these fields can manually be filled or edited after conversion if desired:

metadata = multiscale_v06.model_dump()
metadata["coordinateSystems"][0]["axes"][0]["longName"] = "OpticalAxis"

# And we can update the multiscale metadata model with the edits:

edited_multiscale_v06 = ome_zarr_models.v06.multiscales.Multiscale.model_validate(
    metadata
)
