from pathlib import Path

import graphviz
import zarr

from ome_zarr_models._v06.collection import Collection
from ome_zarr_models._v06.image import Image

graph = graphviz.Digraph("transform-graph")

COLLECTION_PATH = Path(__file__).parent / "stitched_tiles_2d.zarr"
coll = Collection.from_zarr(zarr.open_group(COLLECTION_PATH))

# Systems in root
for system in coll.ome_attributes.coordinateSystems:
    graph.node(name=system.name)

# Transforms in root
for transform in coll.ome_attributes.coordinateTransformations:
    graph.edge(transform.input, transform.output)

# Iterate through multiscale images
for image_path in coll.members:
    image = coll.members[image_path]
    image = Image(members=image.members, attributes=image.attributes)
    image_graph = graphviz.Digraph(
        name=f"cluster_{image_path}",  # node_attr={"shape": "box"}
    )
    # Add this image as an implicit coordinate system
    image_graph.node(f"/{image_path}", fillcolor="#e3a074", style="filled")

    for multiscales in image.ome_attributes.multiscales:
        # Systems in multiscale images
        for system in multiscales.coordinateSystems:
            image_graph.node(name=f"/{image_path}/{system.name}", label=system.name)
        # Transforms in multiscale images
        for dataset in multiscales.datasets:
            for transform in dataset.coordinateTransformations:
                image_graph.edge(
                    f"/{image_path}/{transform.input.removeprefix('/')}",
                    f"/{image_path}/{transform.output.removeprefix('/')}",
                )
        # Add (identity) transform between first coordinate system and path to
        # this multiscales array, since they mean the same thing
        image_graph.edge(
            f"/{image_path}/{multiscales.coordinateSystems[0].name}",
            f"/{image_path}",
        )

    # (implicit) Array coordinate systems
    for array_path in image.members:
        image_graph.node(
            name=f"/{image_path}/{array_path}", fillcolor="#beaed4", style="filled"
        )

    graph.subgraph(image_graph)


graph.render(outfile="transform-graph.png", view=True)
