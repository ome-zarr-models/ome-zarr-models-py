# # Tutorial

import matplotlib.pyplot as plt
import zarr
import zarr.storage
from rich.pretty import pprint

from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v04.image import Image

# ## Loading datasets
#
# OME-Zarr datasets are just zarr groups with special metadata.
# To open an OME-Zarr dataset, we first open the zarr group.

zarr_group = zarr.open(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr", mode="r"
)

# If you're not sure what type or OME-Zarr version of data you have, you can
# use open_ome_zarr() to automatically 'guess' the correct group:

ome_zarr_group = open_ome_zarr(zarr_group)
print(type(ome_zarr_group))
print(ome_zarr_group.ome_zarr_version)

# If you already know the data type you're loading, it's better to load
# directly from that class (see [the API reference](../api/) for a list of classes)
# This will validate the metadata:

ome_zarr_image = Image.from_zarr(zarr_group)

# No errors, which means the metadata is valid 🎉
#
# ## Accessing metadata
# To access the OME-Zarr metadata, use the `.attributes` property:

metadata = ome_zarr_image.attributes
pprint(metadata)

# And as an example of getting more specific metadata, lets get the metadata
# for all the datasets in this multiscales:

pprint(metadata.multiscales[0].datasets)

# ## Accessing data
#
# Although these models do not handle reading or writing data, they do expose the zarr
# arrays. For example, to get the highest resolution image:

zarr_arr = zarr_group[metadata.multiscales[0].datasets[0].path]
pprint(zarr_arr)

# To finish off, lets plot the first z-slice of the first channel of this data:
plt.imshow(zarr_arr[0, 0, :, :], cmap="gray")
