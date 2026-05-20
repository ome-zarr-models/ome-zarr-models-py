# This page explains how to convert metadata from one OME-Zarr version to another.

import zarr.storage
from rich import print

import ome_zarr_models.v05
from ome_zarr_models.v05.multiscales import Extrav06Metadata

# ## 0.5 to 0.6
#
# The main addition to OME-Zarr in version 0.6 is coordinate systems.


zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
image_group_v05 = ome_zarr_models.v05.Image.from_zarr(zarr_group)
multiscales_v05 = image_group_v05.ome_attributes.multiscales[0]
print(multiscales_v05)

# ## Metadata conversion
#
# ome-zarr-models-py offers a convenient way to convert multiscales metadata
# between different OME-Zarr versions. The `Extrav06Metadata` class can be
# used to fill in extra information about multiscales that can be specified
# in version 0.6:

extra_v06_metadata = Extrav06Metadata(
    coordinate_system_name="physical", axes_discrete=[True, True]
)
multiscales_v06 = multiscales_v05.to_version(
    "0.6", extra_v06_metadata=extra_v06_metadata
)
print(multiscales_v06)
