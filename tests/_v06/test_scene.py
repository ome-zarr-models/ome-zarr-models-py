import pytest

from ome_zarr_models import open_ome_zarr
from ome_zarr_models._utils import TransformGraph, TransformGraphNode
from ome_zarr_models._v06 import Scene
from ome_zarr_models._v06.coordinate_transforms import (
    CoordinateSystemIdentifier,
    Translation,
)

SCENE_URL = "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/test-data/v0.6.dev3/idr0050/4995115_output_to_ms.zarr/"


@pytest.mark.vcr
def test_load_scene() -> None:
    scene = open_ome_zarr(SCENE_URL)
    assert isinstance(scene, Scene)
    graph = scene.transform_graph()
    assert graph._graph == {
        TransformGraphNode(
            name="rotated", path="4995115_cropped_400_100_400_400_rot10.zarr"
        ): {
            TransformGraphNode(name="translated_x50", path=None): Translation(
                type="translation",
                input=CoordinateSystemIdentifier(
                    name="rotated", path="4995115_cropped_400_100_400_400_rot10.zarr"
                ),
                output=CoordinateSystemIdentifier(name="translated_x50", path=None),
                name="translate_tile_to_stitched_position",
                translation=(0.0, 0.0, 30.608878192215265, 11.21775638443053),
                path=None,
            )
        },
        TransformGraphNode(
            name="rotated", path="4995115_cropped_700_700_400_400_rot45.zarr"
        ): {
            TransformGraphNode(name="translated_x50", path=None): Translation(
                type="translation",
                input=CoordinateSystemIdentifier(
                    name="rotated", path="4995115_cropped_700_700_400_400_rot45.zarr"
                ),
                output=CoordinateSystemIdentifier(name="translated_x50", path=None),
                name="translate_tile_to_stitched_position",
                translation=(0.0, 0.0, 91.8266345766458, 41.8266345766458),
                path=None,
            )
        },
        TransformGraphNode(name="translated_x50", path=None): {
            TransformGraphNode(name="physical", path="4995115_full.zarr"): Translation(
                type="translation",
                input=CoordinateSystemIdentifier(name="translated_x50", path=None),
                output=CoordinateSystemIdentifier(
                    name="physical", path="4995115_full.zarr"
                ),
                name="translate_tile_to_stitched_position",
                translation=(0.0, 0.0, 0.0, 50.0),
                path=None,
            )
        },
    }


def test_transform_graph() -> None:
    graph = TransformGraph()
    graph.add_transform(
        Translation(
            translation=(1, 2, 3),
            input=CoordinateSystemIdentifier(name="system_1"),
            output=CoordinateSystemIdentifier(name="system_2"),
        )
    )
    graph.add_transform(
        Translation(
            translation=(30, 20, 10),
            input=CoordinateSystemIdentifier(name="system_2"),
            output=CoordinateSystemIdentifier(name="system_3"),
        )
    )

    assert graph.find_shortest_path(
        TransformGraphNode(name="system_1"),
        TransformGraphNode(name="system_3"),
    ) == [
        TransformGraphNode(name="system_1"),
        TransformGraphNode(name="system_2"),
        TransformGraphNode(name="system_3"),
    ]
