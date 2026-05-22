#!/usr/bin/env python3
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import json
from pathlib import Path
import sys
from typing import TypeVar

from ome_zarr_models.v06 import Scene
from ome_zarr_models._utils import TransformGraphNode
import zarr

desc = """
Opens the given Zarr node, parses the contained OME-Zarr metadata,
and applies any coordinate transformations required
to convert the given coordinate array from the source coordinate system to the target.

Prints a JSON object like
'{"coordinates":[[1,2],[3.1,4.1],[5,6]]]}'
in the output system if successful.

Returns a nonzero exit code and may print a JSON object like
'{"message": "could not parse OME-Zarr metadata"}'
on failure.
"""


def parse_input_coords(s: str) -> list[list[float]]:
    """Parse a JSON string of coordinates."""
    jso = json.loads(s)
    if not isinstance(jso, list):
        raise ValueError("Input coordinates are not a list")
    out = []
    for coord in jso:
        if not isinstance(coord, list):
            raise ValueError("Input coordinates are not lists")
        out.append([float(elem) for elem in coord])
    return out


T = TypeVar("T")


def pairs(lst: list[T]):
    """Sliding window of length 2."""
    if len(lst) < 2:
        return
    it = iter(lst)
    next(it)
    yield from zip(lst, it, strict=False)


def main():
    """Main function."""
    parser = ArgumentParser(
        description=desc,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        type=Path,
        help="path to an OME-Zarr hierarchy on the file system with Scene metadata",
    )
    parser.add_argument(
        "source",
        metavar="SOURCE",
        help="name of a source coordinate system defined in the OME-Zarr Scene",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="name of a target coordinate system defined in the OME-Zarr Scene",
    )
    parser.add_argument(
        "coordinates",
        metavar="COORDINATES",
        type=parse_input_coords,
        help="JSON-serialised array of coordinate arrays; e.g. 3 coordinates in 2D space '[[1,2],[3.1,4.1],[5,6]]'",
    )

    args = parser.parse_args()

    scene = Scene.from_zarr(zarr.open_group(args.path, mode="r"))
    g = scene.transform_graph()
    src = TransformGraphNode(name=args.source)
    tgt = TransformGraphNode(name=args.target)
    seq = g.find_shortest_path(src, tgt)

    if seq is None:
        print(json.dumps({"message": f"no path found {args.source}->{args.target}"}))
        return 1

    out = []

    for c in args.coordinates:
        for s1, s2 in pairs(seq):
            t = g._graph[s1][s2]
            c = t.transform_point(c)
        out.append(list(c))

    print(json.dumps({"coordinates": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
