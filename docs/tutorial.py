# # Tutorial

import matplotlib.pyplot as plt
import zarr
import zarr.storage
from rich.pretty import pprint

from ome_zarr_models.data import tutorial_data_path
from ome_zarr_models.v04 import Image

# ## Loading datasets
#
# OME-zarr datasets are just zarr groups with special metadata.
# To open an OME-zarr dataset, we first open the zarr group, and
# then create an image object from it. This will validate the
# metadata.

group = zarr.open(tutorial_data_path)
ome_zarr_image = Image(group=group)
pprint(ome_zarr_image)

# No errors, which means the metadata is valid 🎉
#
# ## Accessing metadata
# To access the OME-zarr metadata, use the `.attributes` property:

metadata = ome_zarr_image.attributes
pprint(metadata)
pprint(metadata.multiscales[0].datasets)

# ## Accessing data
#
# Although these models do not handle reading or writing data, they do expose the zarr
# arrays. For example, to get the highest resolution image:

zarr_arr = ome_zarr_image.group[metadata.multiscales[0].datasets[0].path]
pprint(zarr_arr)
plt.imshow(zarr_arr, cmap="gray")
