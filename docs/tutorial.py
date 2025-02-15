# # Tutorial

import os
import tempfile

import matplotlib.pyplot as plt
import zarr
import zarr.storage
from rich.pretty import pprint

from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v04.axes import Axis
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

# ## Creating new datasets
#
# To create new OME-Zarr datasets, the ``.new()`` method on the OME-Zarr groups
# can be used.
#
# As an example we'll create an OME-Zarr image with two arrays, one at the
# original resolution and one downsampled version.

arrays = [zarr.empty(shape=(100, 100)), zarr.empty(shape=(50, 50))]
pixel_size = (6, 4)
pixel_unit = "um"

ome_zarr_image = Image.new(
    arrays=arrays,
    paths=["level0", "level1"],
    axes=[
        Axis(name="y", type="space", unit=pixel_unit),
        Axis(name="x", type="space", unit=pixel_unit),
    ],
    global_scale=pixel_size,
    scales=[(1, 1), (2, 2)],
    translations=[(0, 0), (3, 2)],
)
print(ome_zarr_image)

# ## Saving datasets
#
# To save a new dataset the ``.to_zarr(store=...)`` method can be used,
# which will put all the OME-Zarr group metadata into a Zarr store.
#
# In this tutorial we'll use a temporary directory to save the Zarr group
# to:

with tempfile.TemporaryDirectory() as fp:
    store = zarr.DirectoryStore(path=fp)
    ome_zarr_image.to_zarr(store=store, path="/")
    print(os.listdir(fp))
