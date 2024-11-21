# # Tutorial

from rich.pretty import pprint


from itkwidgets import view
import gcsfs
import zarr
import zarr.storage

from ome_zarr_models.v04 import Image
from ome_zarr_models.v04.coordinate_transformations import (
    VectorTranslation,
)

# ## Creating models
#
# We can create an Image model from a zarr group, that points to an
# OME-zarr dataset:

# Setup zarr group from a remote store
bucket = "ucl-hip-ct-35a68e99feaae8932b1d44da0358940b"
fs = gcsfs.GCSFileSystem(project=bucket, token="anon", access="read_only")
store = zarr.storage.FSStore(url=bucket, fs=fs)
group = zarr.open_group(
    store=store, path="S-20-28/heart/25.27um_complete-organ_bm05.ome.zarr"
)

ome_zarr_image = Image(group)

# Oh no, it failed! One of the key goals of this package is to eagerly validatemetadata, so you can realise it's wrong.
#
# Lets try that again, but with some valid OME-zarr data

group = zarr.open("https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr")
ome_zarr_image = Image(group)
pprint(ome_zarr_image)

# This image contains both the zarr group, and a model of the multiscales metadata

multiscales_meta = ome_zarr_image.multiscales
pprint(multiscales_meta)

# ## Updating models
#
# All the fields in the models can be updated in place. When you do this, any validation on the individual field you are updating will take place.
#
# For example, there is no name for the first multiscales entry, so lets add it

multiscales_meta[0].name = "The first multiscales entry"
pprint(multiscales_meta)

# One constraint in the OME-zarr spec is that the coordiante transforms have to be a scale, or a scale then tranlsation (strictly in that order). So if we try and make a transformation just a translation, it will raise an error.

multiscales_meta[0].datasets[0].coordinateTransformations = VectorTranslation(
    type="translation", translation=[1, 2, 3]
)


# This means validation happens early, allowing you to catch errors
# before getting too far.

# ## Writing metadata
#
# To save the metadata after editing, we can use the ``save_attrs()`` method.
# TODO: Use a local file for testing that we have write access to, so we
# can demonstrate this.
#

# +
# ome_zarr_image.save_attrs()
# -

# ## Accessing data
#
# Although these models do not handle reading or writing data, they do expose the zarr arrays.

zarr_arr = ome_zarr_image.group[multiscales_meta[0].datasets[-1].path]
pprint(zarr_arr)
view(zarr_arr)

# ## Not using validation
#
# If you want to create models that are not validated against the OME-zarr specifciation, you can use the ``model_construct`` method on the models.
