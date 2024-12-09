# # Tutorial

import zarr
import zarr.storage
from rich.pretty import pprint

from ome_zarr_models.data import tutorial_data_path
from ome_zarr_models.v04 import Image2
# ## Creating models
#
# We can create an Image model from a zarr group, that points to an
# OME-zarr dataset:

print(tutorial_data_path.absolute())
group = zarr.open(tutorial_data_path)
ome_zarr_image = Image2(group=group)
pprint(ome_zarr_image)

# This image contains only the zarr group. To get a copy of the attributes,
# we can access the `.attributes` property

metadata = ome_zarr_image.attributes
pprint(metadata)

# ## Accessing data
#
# Although these models do not handle reading or writing data, they do expose the zarr
# arrays.

zarr_arr = ome_zarr_image.group[metadata.multiscales[0].datasets[0].path]
pprint(zarr_arr)

# ## Not using validation
#
# If you want to create models that are not validated against the OME-zarr
# specifciation, you can use the ``model_construct`` method on the models.
