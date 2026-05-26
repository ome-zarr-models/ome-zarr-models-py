# This page explains how to convert metadata from one OME-Zarr version to another.
#
# ## 0.5 to 0.6
#
# The main addition to OME-Zarr in version 0.6 is coordinate systems.


import zarr.storage
from rich import print

import ome_zarr_models.v05
import ome_zarr_models.v06

zarr_group = zarr.open_group(
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.5/idr0066/ExpD_chicken_embryo_MIP.ome.zarr",
    mode="r",
)
image_group_v05 = ome_zarr_models.v05.Image.from_zarr(zarr_group)
print(image_group_v05.ome_attributes)

# ## Metadata conversion
#
# ome-zarr-models-py offers a convenient way to convert multiscales metadata
# between different ome-zarr versions without using the high-level
# `Image` classes:

multiscale = ome_zarr_models.v05.multiscales.Multiscale.model_validate(
    {
        "axes": [
            {"name": "z", "type": "space"},
            {"name": "y", "type": "space"},https://app.gather.town/app/nq1oQrNJ1UIQ5t01/imagesc-island
            {"name": "x", "type": "space"},
        ],
        "datasets": [  # an image with a single resolution level
            {
                "path": "s0",
                "coordinateTransformations": [
                    {
                        "type": "scale",
                        "scale": [1, 1, 1],
                    }
                ],
            }
        ],
        "name": "my_image",
    }
)

multiscale_v06 = multiscale.to_version("0.6")
print(multiscale_v06)

# The 0.6 specification provides some new fields over the 0.5 version,
# such as the `coordinateSystems` field,
# which provides named coordinate system references.
# 
# In the process of conversion, these new fields are provided with default values
# (i.e., the `name` of the default coordinate system is set to "physical").
# However, these fields can manually be filled or edited after conversion if desired:

coordinate_system = multiscale_v06.coordinateSystems[0]
print(coordinate_system)

# Now we can edit the coordinate system name:

edited_coordinate_system = coordinate_system.model_copy(
  update={"name": "my_coordinate_system"})
print(edited_coordinate_system)

# And we can update the multiscale metadata with the edited coordinate system:

edited_multiscale_v06 = multiscale_v06.model_copy(
    update={"coordinateSystems": [edited_coordinate_system]}
)

# This version conversion works between all currently supported versions of ome-zarr:

multiscale_v04 = multiscale.to_version("0.4")
print(multiscale_v04)
