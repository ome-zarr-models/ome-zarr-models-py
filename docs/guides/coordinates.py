# This guide explains how coordinate systems and transforms work in OME-Zarr
# and `ome-zarr-models`.
#
# Let's start by loading an example scene dataset. A Scene is a OME-Zarr dataset
# that contains coordinate systems and transforms between these systems.
# The inputs or outputs to the transforms can be systems or image arrays
# that are subgroups of the Scene Zarr group.

import zarr
from IPython.display import SVG, display
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
#
# The input to the first two coordinate transforms contain `path` fields.
# These refer to OME-Zarr image groups stored a Zarr subgroups under the
# Scene group.
#
# This can be verified using the `.images` property to see available images:

print("Images making up the scene:")
print(scene.images.keys())

# The individual images can also contain their own coordinate transforms and systems.
#
# To get a better overview of the complete set of coordinate systems and transforms
# we can visualize them as a graph where the nodes are systems, connected by
# directed vertices (arrows) representing the transforms.
#
# In `ome-zarr-models` you can do this by getting a transform graph:

transform_graph = scene.transform_graph()
print(transform_graph)

# To visualize,

svg_string = transform_graph.to_graphviz().pipe(format="svg")
display(SVG(data=svg_string))
