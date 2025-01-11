from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.coordinate_transformations import VectorScale
from ome_zarr_models.v04.image import Image, ImageAttrs
from ome_zarr_models.v04.multiscales import Dataset, Multiscale
from tests.v04.conftest import json_to_zarr_group


def test_image() -> None:
    zarr_group = json_to_zarr_group(json_fname="multiscales_example.json")
    zarr_group.create_dataset("0", shape=(1, 1, 1, 1))
    zarr_group.create_dataset("1", shape=(1, 1, 1, 1))

    ome_group = Image.from_zarr(zarr_group)
    assert ome_group.attributes == ImageAttrs(
        multiscales=[
            Multiscale(
                axes=[
                    Axis(name="c", type="channel", unit=None),
                    Axis(name="z", type="space", unit="micrometer"),
                    Axis(name="y", type="space", unit="micrometer"),
                    Axis(name="x", type="space", unit="micrometer"),
                ],
                datasets=(
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            VectorScale(
                                type="scale",
                                scale=[
                                    1.0,
                                    0.5002025531914894,
                                    0.3603981534640209,
                                    0.3603981534640209,
                                ],
                            ),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            VectorScale(
                                type="scale",
                                scale=[
                                    1.0,
                                    0.5002025531914894,
                                    0.7207963069280418,
                                    0.7207963069280418,
                                ],
                            ),
                        ),
                    ),
                ),
                version="0.4",
                coordinateTransformations=None,
                metadata=None,
                name=None,
                type=None,
            )
        ],
        omero=None,
        _creator={"name": "omero-zarr", "version": "0.4.0"},
    )
