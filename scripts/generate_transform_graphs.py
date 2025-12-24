"""
Generate transform graphs for each of the RFC-5 examples.
"""

from pathlib import Path

import zarr

from ome_zarr_models._v06.image import Image
from ome_zarr_models._v06.scene import Scene

EXAMPLE_PATH = (
    Path(__file__).parent.parent
    / "tests"
    / "_v06"
    / "rfc5"
    / "transform_examples"
    / "ngff-rfc5-coordinate-transformation-examples"
)

OUTPUT_PATH = Path(
    "/Users/dstansby/software/ome-zarr/rfc5-example-transform-graphs/graphs"
)
OUTPUT_PATH.mkdir(exist_ok=True)


def get_all_zarrs(directory: Path) -> list[Path]:
    """
    Get all Zarr sub-directories.
    """
    zarrs: list[Path] = []
    for f in directory.glob("*"):
        if f.is_dir():
            if f.suffix == ".zarr":
                # Found a Zarr group
                zarrs.append(f)
            else:
                # Recurse
                zarrs += get_all_zarrs(f)

    return sorted(zarrs)


for zarr_path in get_all_zarrs(EXAMPLE_PATH):
    relative_path = zarr_path.relative_to(EXAMPLE_PATH)
    graph_path = OUTPUT_PATH / relative_path.parent
    graph_path.mkdir(exist_ok=True, parents=True)

    group: Scene | Image
    try:
        if relative_path.parts[0] == "user_stories":
            group = Scene.from_zarr(zarr.open_group(zarr_path, mode="r"))
        else:
            group = Image.from_zarr(zarr.open_group(zarr_path, mode="r"))
    except Exception:
        print(f"😢 Failed to load group at {zarr_path.relative_to(EXAMPLE_PATH)}")
        continue

    print(f"📈 Rendering transform graph for {zarr_path.relative_to(EXAMPLE_PATH)}")
    graph = group.transform_graph()
    graphviz_graph = graph.to_graphviz()
    graphviz_graph.render(
        filename=zarr_path.name.removesuffix(".zarr"),
        directory=graph_path,
        cleanup=True,
        format="png",
    )

print(f"Rendered graphs available at {OUTPUT_PATH}")
