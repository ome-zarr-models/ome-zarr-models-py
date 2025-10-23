"""
Generate transform graphs for each of the RFC-5 examples.
"""

from pathlib import Path

import zarr

from ome_zarr_models._v06.image import Image

EXAMPLE_PATH = Path("/Users/dstansby/software/ome-zarr/rfc5-example-transform-graphs")

OUTPUT_PATH = Path(__file__).parent / "graphs"
OUTPUT_PATH.mkdir(exist_ok=True)

for subdir in [p for p in EXAMPLE_PATH.iterdir() if p.is_dir()]:
    for sub_subdir in [p for p in subdir.iterdir() if p.is_dir()]:
        graph_path = OUTPUT_PATH / subdir.name / sub_subdir.name
        graph_path.mkdir(exist_ok=True, parents=True)

        for image_path in sub_subdir.glob("*.zarr"):
            try:
                image = Image.from_zarr(zarr.open_group(image_path, mode="r"))
            except Exception:
                print(
                    f"😢 Failed to load group at {image_path.relative_to(EXAMPLE_PATH)}"
                )
                continue

            print(
                f"📈 Rendering transform graph for {image_path.relative_to(EXAMPLE_PATH)}"
            )
            graph = image.transform_graph()
            graphviz_graph = graph.to_graphviz()
            graphviz_graph.render(
                filename=image_path.name.removesuffix(".zarr"),
                directory=graph_path,
                cleanup=True,
                format="png",
            )
