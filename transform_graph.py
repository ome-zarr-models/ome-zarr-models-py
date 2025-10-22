from pathlib import Path

import graphviz
import zarr

from ome_zarr_models._v06.collection import Collection
from ome_zarr_models._v06.image import Image

dot = graphviz.Digraph("transform-graph")

COLLECTION_PATH = Path(__file__).parent / "stitched_tiles_2d.zarr"
coll = Collection.from_zarr(zarr.open_group(COLLECTION_PATH))

# Systems in root
for system in coll.ome_attributes.coordinateSystems:
    dot.node(name=system.name)

# Transforms in root
for transform in coll.ome_attributes.coordinateTransformations:
    dot.edge(transform.input, transform.output)

# Iterate through multiscale images
for image_path in coll.members:
    image = coll.members[image_path]
    image = Image(members=image.members, attributes=image.attributes)
    for multiscales in image.ome_attributes.multiscales:
        # Systems in multiscale images
        for system in multiscales.coordinateSystems:
            dot.node(name=system.name)
        for dataset in multiscales.datasets:
            for transform in dataset.coordinateTransformations:
                dot.edge(
                    transform.input,
                    transform.output,
                )

    # (implicit) Array coordinate systems
    for array_path in image.members:
        dot.node(
            name=f"/{image_path}/{array_path}",
        )


dot.render(outfile="transform-graph.png", view=True)
