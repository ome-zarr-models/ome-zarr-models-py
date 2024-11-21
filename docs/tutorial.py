# # Tutorial

# from ome_zarr_models.v04 import Image as OMEZarrImage

# my_image = OMEZarrImage(path="path/to/ome/zarr/directory.ome.zarr")
# print(my_image.multiscales)

# ## Creating
#
# TODO: exmaple of creating a model from a remote store
# TODO: example of

import gcsfs
import zarr.storage
import zarr

bucket = "ucl-hip-ct-35a68e99feaae8932b1d44da0358940b"
fs = gcsfs.GCSFileSystem(project=bucket, token="anon", access="read_only")
store = zarr.storage.FSStore(url=bucket, fs=fs)
group = zarr.open_group(
    store=store, path="S-20-28/heart/25.27um_complete-organ_bm05.ome.zarr"
)
print(group)
exit()

# ## Updating models
#
# All the fields in the models can be updated in place.
# When you do this, any validation on the individual field
# you are updating will take place.
#
# For example, we can [do something valid]:


# but if you try and [do something invalid] it raises an error:

# This means validation happens early, allowing you to catch errors
# before getting too far.

# ## Writing metadata
#
# TODO: example of writing out the metadata again

# ## Accessing data
#
# Although these models do not handle reading or writing data,
# they do expose the zarr arrays.

# ## Not using validation
#
# If you *really* want to create models that are not validated against
# the OME-zarr specifciation, you can use the ``model_construct`` method.
# For example:

# Put some bad code here
