import json
from pathlib import Path

from ome_zarr_models.v04.image import (
    Axis,
    CoordinateTransforms,
    Dataset,
    MultiscaleMetadata,
    MultiscaleMetadatas,
    ScaleTransform,
)


def test_multiscale_metadata():
    with open(Path(__file__).parent / "data" / "spec_example_multiscales.json") as f:
        json_data = json.load(f)

    metadatas = MultiscaleMetadatas._from_json(json_data)
    print(metadatas)
    assert metadatas == MultiscaleMetadatas(
        multiscales=[
            MultiscaleMetadata(
                axes=(
                    Axis(name="t", type="time", unit="millisecond"),
                    Axis(name="c", type="channel", unit=None),
                    Axis(name="z", type="space", unit="micrometer"),
                    Axis(name="y", type="space", unit="micrometer"),
                    Axis(name="x", type="space", unit="micrometer"),
                ),
                datasets=[
                    Dataset(
                        path="0",
                        coordinateTransformations=CoordinateTransforms(
                            scale=ScaleTransform(
                                type="scale", scale=[1.0, 1.0, 0.5, 0.5, 0.5]
                            ),
                            translation=None,
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=CoordinateTransforms(
                            scale=ScaleTransform(
                                type="scale", scale=[1.0, 1.0, 1.0, 1.0, 1.0]
                            ),
                            translation=None,
                        ),
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=CoordinateTransforms(
                            scale=ScaleTransform(
                                type="scale", scale=[1.0, 1.0, 2.0, 2.0, 2.0]
                            ),
                            translation=None,
                        ),
                    ),
                ],
                coordinateTransformations=CoordinateTransforms(
                    scale=ScaleTransform(type="scale", scale=[0.1, 1.0, 1.0, 1.0, 1.0]),
                    translation=None,
                ),
                name="example",
                version="0.4",
                metadata={
                    "description": "the fields in metadata depend on the downscaling implementation. Here, the parameters passed to the skimage function are given",
                    "method": "skimage.transform.pyramid_gaussian",
                    "version": "0.16.1",
                    "args": "[true]",
                    "kwargs": {"multichannel": True},
                },
                type="gaussian",
            )
        ]
    )
