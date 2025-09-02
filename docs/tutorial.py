# # Tutorial
#
# This tutorial provides a full worked example of using `ome-zarr-models`
import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import zarr
import zarr.storage
from pydantic_zarr.v3 import AnyArraySpec, ArraySpec, NamedConfig
from rich.pretty import pprint

from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v05.axes import Axis
from ome_zarr_models.v05.image import Image

# ## Loading datasets
#
# OME-Zarr datasets are Zarr groups with specific metadata.
# To open an OME-Zarr dataset, we first open the Zarr group.

zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
# If you're not sure what type or OME-Zarr version of data you have, you can
# use `open_ome_zarr()` to automatically 'guess' the correct group:

ome_zarr_group = open_ome_zarr(zarr_group)
print(f"Group class: {type(ome_zarr_group)}")
print(f"OME-Zarr version: {ome_zarr_group.ome_zarr_version}")

# If you already know the data type you're loading, it's better to load
# directly from that class (see [the API reference](../api/) for a list of classes)
# This will validate the metadata:

ome_zarr_image = Image.from_zarr(zarr_group)

# No errors, which means the metadata is valid 🎉
#
# ## Accessing metadata
# To access the OME-Zarr metadata, use the `.ome_attributes` property:

metadata = ome_zarr_image.ome_attributes
pprint(metadata)

# And as an example of getting more specific metadata, lets get the metadata
# for all the datasets in this multiscales:

pprint(ome_zarr_image.datasets[0])

# ## Accessing data
#
# Although these models do not handle reading or writing data, they do give access to
# the Zarr arrays using the `zarr-python` library.
# For example, to get the highest resolution image:

zarr_arr = zarr_group[ome_zarr_image.datasets[0][3].path]
pprint(zarr_arr)

# To finish off this section on accessing data, lets plot this image:

plt.imshow(zarr_arr, cmap="gray")

# ## Creating new datasets
#
# To create new OME-Zarr datasets, the `.new()` method on the OME-Zarr groups
# can be used. This creates all the Zarr groups, Zarr arrays within those groups,
# and related metadata, but does not write any data to the Zarr arrays.
#
# As an example we'll create an OME-Zarr image with two arrays, one at the
# original resolution and one downsampled version.
#
# First, we need to create `ArraySpec` objects, which tell `ome-zarr-models`
# what the structure of the data arrays will be.


array_specs: list[AnyArraySpec] = [
    ArraySpec(
        shape=(100, 100),
        data_type=np.uint16,
        chunk_grid=NamedConfig(
            name="regular",
            configuration={"chunk_shape": [32, 32]},
        ),
        chunk_key_encoding=NamedConfig(
            name="default", configuration={"separator": "/"}
        ),
        fill_value=0,
        codecs=[NamedConfig(name="bytes")],
        dimension_names=["y", "x"],
    ),
    ArraySpec(
        shape=(100, 100),
        data_type=np.uint16,
        chunk_grid=NamedConfig(
            name="regular",
            configuration={"chunk_shape": [32, 32]},
        ),
        chunk_key_encoding=NamedConfig(
            name="default", configuration={"separator": "/"}
        ),
        fill_value=0,
        codecs=[NamedConfig(name="bytes")],
        dimension_names=["y", "x"],
    ),
]

# Next, we'll set some metadata values

pixel_size = (6, 4)
pixel_unit = "um"

# Finally, we can use these variables to create a new OME-Zarr image group.

ome_zarr_image = Image.new(
    array_specs=array_specs,
    paths=["level0", "level1"],
    axes=[
        Axis(name="y", type="space", unit=pixel_unit),
        Axis(name="x", type="space", unit=pixel_unit),
    ],
    scales=[[p * 1 for p in pixel_size], [p * 2 for p in pixel_size]],
    translations=[[0, 0], [p * 0.5 for p in pixel_size]],
)
pprint(ome_zarr_image)

# It's also possible to create array metadata from existing arrays.
#
# For numpy arrays:

arr0 = np.zeros(shape=(100, 100), dtype=np.uint16)
arr1 = np.zeros(shape=(50, 50), dtype=np.uint16)
array_specs = [ArraySpec.from_array(arr0), ArraySpec.from_array(arr1)]

# or for Zarr arrays:

arr_zarr0 = zarr.zeros(shape=(100, 100), dtype=np.uint16, zarr_format=2)
arr_zarr1 = zarr.zeros(shape=(50, 50), dtype=np.uint16, zarr_format=2)
array_specs = [ArraySpec.from_array(arr_zarr0), ArraySpec.from_array(arr_zarr1)]

# ## Saving datasets
#
# At this point the `ome_zarr_image` object is a representation of the
# OME-Zarr group in the memory of your computer.
#
# To save a new dataset the ``.to_zarr(store=...)`` method can be used,
# which will put all the OME-Zarr group metadata into a Zarr store.
#
# In this tutorial we'll use a temporary directory to save the Zarr group
# to, and then list the directory to show that it has been saved.

with tempfile.TemporaryDirectory() as fp:
    store = zarr.storage.LocalStore(fp)
    ome_zarr_image.to_zarr(store=store, path="/")
    print(os.listdir(fp))
