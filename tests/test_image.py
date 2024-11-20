import json
from pathlib import Path

from ome_zarr_models.v04.image import Dataset, MultiscaleMetadata, MultiscaleMetadatas


def test_multiscale_metadata():
    with open(Path(__file__).parent / "data" / "spec_example_multiscales.json") as f:
        json_data = json.load(f)

    metadatas = MultiscaleMetadatas.from_json(json_data)
    print(metadatas)
    assert metadatas == MultiscaleMetadatas(
        multiscales=[
            MultiscaleMetadata(
                axes=[
                    {"name": "t", "type": "time", "unit": "millisecond"},
                    {"name": "c", "type": "channel"},
                    {"name": "z", "type": "space", "unit": "micrometer"},
                    {"name": "y", "type": "space", "unit": "micrometer"},
                    {"name": "x", "type": "space", "unit": "micrometer"},
                ],
                datasets=[
                    Dataset(
                        path="0",
                        coordinateTransformations=[
                            {"type": "scale", "scale": [1.0, 1.0, 0.5, 0.5, 0.5]}
                        ],
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=[
                            {"type": "scale", "scale": [1.0, 1.0, 1.0, 1.0, 1.0]}
                        ],
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=[
                            {"type": "scale", "scale": [1.0, 1.0, 2.0, 2.0, 2.0]}
                        ],
                    ),
                ],
                coordinateTransformations=[
                    {"type": "scale", "scale": [0.1, 1.0, 1.0, 1.0, 1.0]}
                ],
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
