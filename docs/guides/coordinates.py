# This guide explains how coordinate systems and transforms work in OME-Zarr
# and `ome-zarr-models`.
#
# Let's start by loading an example scene dataset. A Scene is a OME-Zarr dataset
# that contains coordinate systems and transforms between these systems.
# The inputs or outputs to the transforms can be systems or image arrays
# that are subgroups of the Scene Zarr group.

import zarr
from rich import print

from ome_zarr_models._v06 import Scene

scene = Scene.from_zarr(
    zarr.open_group(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/test-data/v0.6.dev3/idr0050/4995115_output_to_ms.zarr/",
        mode="r",
    )
)

print(scene.ome_attributes)

# Here we can see that the scene metadata defines one coordinate system and
# three coordinate transforms.
