# This page explains how to convert metadata from one OME-Zarr version to another.
#

import zarr.storage
from rich import print

import ome_zarr_models.v05
import ome_zarr_models.v06

# ## 0.5 to 0.6
#
# The main addition to OME-Zarr in version 0.6 is coordinate systems for images.
# This example shows how to convert OME-Zarr 0.5 image metadata to OME-Zarr 0.6.
#
# To start we'll open a OME-Zarr 0.5 image, and extract the OME-Zarr image metadata.

zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
image_group_v05 = ome_zarr_models.v05.Image.from_zarr(zarr_group)
image_attributes_v05 = image_group_v05.ome_attributes
print(image_attributes_v05)


# Next we'll convert this metadata to version 0.6.

image_attributes_v06 = image_attributes_v05.to_version(
    "0.6", default_cs_name="intrinsic"
)
print(image_attributes_v06)

# With the new metadata, we can create a full Image model.
# This Image can then be saved using the `to_zarr()` method.
# Because it does not contain any array data or metadata, the
# array data will need to be manually copied from the old 0.5
# group to the new 0.6 group.

image_v06 = ome_zarr_models.v06.Image(
    members=image_group_v05.members, attributes={"ome": image_attributes_v06}
)
# image_v06.to_zarr(...)

# The 0.6 specification provides some new fields over the 0.5 version,
# such as the `coordinateSystems` field,
# which provides named coordinate system references.
#
# In the process of conversion, these new fields are provided with default values
# (i.e., the `name` of the default coordinate system is set to "physical").
# However, these fields can manually be filled or edited after conversion if desired.
# The easiest way to do this is convert the model to a dictionary, edit it,
# and then read it in again to a model (which will validate the new metadata)

image_metadata_v06 = image_v06.ome_attributes.model_dump()
image_metadata_v06["multiscales"][0]["coordinateSystems"][0]["axes"][0]["longName"] = (
    "OpticalAxis"
)
image_attributes_v06 = ome_zarr_models.v06.image.ImageAttrs.model_validate(
    image_metadata_v06
)
