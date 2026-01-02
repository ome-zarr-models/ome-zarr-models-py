import pytest
import zarr
from pydantic_zarr.v2 import ArraySpec, GroupSpec

from ome_zarr_models.v04.bioformats2raw import BioFormats2Raw, BioFormats2RawAttrs
from ome_zarr_models.v04.image import Image
from ome_zarr_models.v04.plate import (
    Acquisition,
    Column,
    Plate,
    Row,
    WellInPlate,
)
from tests.v04.conftest import read_in_json


def test_bioformats2raw_example_json() -> None:
    model = read_in_json(
        json_fname="bioformats2raw_example.json", model_cls=BioFormats2RawAttrs
    )

    assert model == BioFormats2RawAttrs(
        bioformats2raw_layout=3,
        plate=Plate(
            acquisitions=[
                Acquisition(id=0, maximumfieldcount=None, name=None, description=None)
            ],
            columns=[Column(name="1")],
            field_count=1,
            name="Plate Name 0",
            rows=[Row(name="A")],
            version="0.4",
            wells=[WellInPlate(path="A/1", rowIndex=0, columnIndex=0)],
        ),
        series=None,
    )


@pytest.mark.vcr
def test_bioformats2raw_get_image() -> None:
    zarr_grp = zarr.open_group(
        "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0079A/idr0079_images.zarr",
        mode="r",
    )
    model = BioFormats2Raw.from_zarr(zarr_grp)
    assert model.ome_attributes == BioFormats2RawAttrs(
        bioformats2raw_layout=3, plate=None, series=None
    )
    assert model.image_paths == ["0", "1", "2"]
    assert model.images == {
        "0": Image(
            zarr_format=2,
            attributes={
                "multiscales": [
                    {
                        "axes": [
                            {"name": "c", "type": "channel", "unit": None},
                            {"name": "z", "type": "space", "unit": "micrometer"},
                            {"name": "y", "type": "space", "unit": "micrometer"},
                            {"name": "x", "type": "space", "unit": "micrometer"},
                        ],
                        "datasets": (
                            {
                                "path": "0",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.1024427, 0.1024427],
                                    },
                                ),
                            },
                            {
                                "path": "1",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.2048854, 0.2048854],
                                    },
                                ),
                            },
                            {
                                "path": "2",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.4097708, 0.4097708],
                                    },
                                ),
                            },
                            {
                                "path": "3",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.8195416, 0.8195416],
                                    },
                                ),
                            },
                            {
                                "path": "4",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 1.6390832, 1.6390832],
                                    },
                                ),
                            },
                            {
                                "path": "5",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 3.2781664, 3.2781664],
                                    },
                                ),
                            },
                        ),
                        "metadata": None,
                        "name": "9836998.ome.zarr",
                        "type": None,
                        "version": "0.4",
                    }
                ],
                "omero": {
                    "channels": [
                        {
                            "color": "00FF00",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 3.0,
                                "end": 246.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "lynEGFP",
                        },
                        {
                            "color": "FF0000",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 6.0,
                                "end": 133.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "NLStdTomato",
                        },
                    ],
                    "id": 1,
                    "rdefs": {"defaultT": 0, "defaultZ": 71, "model": "color"},
                    "version": "0.4",
                },
                "_creator": {
                    "name": "omero-zarr",
                    "version": "0.5.6.dev59+g03d46b2.d20250610",
                },
            },
            members={
                "labels": GroupSpec(
                    zarr_format=2, attributes={"labels": ["0"]}, members={}
                ),
                "0": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 788, 1584),
                    chunks=(1, 1, 1024, 1024),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "1": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 394, 792),
                    chunks=(1, 1, 394, 792),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "2": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 197, 396),
                    chunks=(1, 1, 197, 396),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "3": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 98, 198),
                    chunks=(1, 1, 98, 198),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "4": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 49, 99),
                    chunks=(1, 1, 49, 99),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "5": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 142, 24, 49),
                    chunks=(1, 1, 24, 49),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
            },
        ),
        "1": Image(
            zarr_format=2,
            attributes={
                "multiscales": [
                    {
                        "axes": [
                            {"name": "c", "type": "channel", "unit": None},
                            {"name": "z", "type": "space", "unit": "micrometer"},
                            {"name": "y", "type": "space", "unit": "micrometer"},
                            {"name": "x", "type": "space", "unit": "micrometer"},
                        ],
                        "datasets": (
                            {
                                "path": "0",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.1024427, 0.1024427],
                                    },
                                ),
                            },
                            {
                                "path": "1",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.2048854, 0.2048854],
                                    },
                                ),
                            },
                            {
                                "path": "2",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.4097708, 0.4097708],
                                    },
                                ),
                            },
                            {
                                "path": "3",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.8195416, 0.8195416],
                                    },
                                ),
                            },
                            {
                                "path": "4",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 1.6390832, 1.6390832],
                                    },
                                ),
                            },
                            {
                                "path": "5",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 3.2781664, 3.2781664],
                                    },
                                ),
                            },
                        ),
                        "metadata": None,
                        "name": "9837019.ome.zarr",
                        "type": None,
                        "version": "0.4",
                    }
                ],
                "omero": {
                    "channels": [
                        {
                            "color": "00FF00",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 2.0,
                                "end": 231.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "lynEGFP",
                        },
                        {
                            "color": "FF0000",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 17.0,
                                "end": 246.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "NLStdTomato",
                        },
                    ],
                    "id": 1,
                    "rdefs": {"defaultT": 0, "defaultZ": 70, "model": "color"},
                    "version": "0.4",
                },
                "_creator": {
                    "name": "omero-zarr",
                    "version": "0.5.6.dev59+g03d46b2.d20250610",
                },
            },
            members={
                "0": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 788, 1584),
                    chunks=(1, 1, 1024, 1024),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "1": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 394, 792),
                    chunks=(1, 1, 394, 792),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "2": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 197, 396),
                    chunks=(1, 1, 197, 396),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "3": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 98, 198),
                    chunks=(1, 1, 98, 198),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "4": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 49, 99),
                    chunks=(1, 1, 49, 99),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "5": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 140, 24, 49),
                    chunks=(1, 1, 24, 49),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
            },
        ),
        "2": Image(
            zarr_format=2,
            attributes={
                "multiscales": [
                    {
                        "axes": [
                            {"name": "c", "type": "channel", "unit": None},
                            {"name": "z", "type": "space", "unit": "micrometer"},
                            {"name": "y", "type": "space", "unit": "micrometer"},
                            {"name": "x", "type": "space", "unit": "micrometer"},
                        ],
                        "datasets": (
                            {
                                "path": "0",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.1024427, 0.1024427],
                                    },
                                ),
                            },
                            {
                                "path": "1",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.2048854, 0.2048854],
                                    },
                                ),
                            },
                            {
                                "path": "2",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.4097708, 0.4097708],
                                    },
                                ),
                            },
                            {
                                "path": "3",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 0.8195416, 0.8195416],
                                    },
                                ),
                            },
                            {
                                "path": "4",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 1.6390832, 1.6390832],
                                    },
                                ),
                            },
                            {
                                "path": "5",
                                "coordinateTransformations": (
                                    {
                                        "type": "scale",
                                        "scale": [1.0, 0.2245383, 3.2781664, 3.2781664],
                                    },
                                ),
                            },
                        ),
                        "metadata": None,
                        "name": "9837025.ome.zarr",
                        "type": None,
                        "version": "0.4",
                    }
                ],
                "omero": {
                    "channels": [
                        {
                            "color": "00FF00",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 1.0,
                                "end": 251.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "lynEGFP",
                        },
                        {
                            "color": "FF0000",
                            "window": {
                                "max": 255.0,
                                "min": 0.0,
                                "start": 13.0,
                                "end": 109.0,
                            },
                            "active": True,
                            "coefficient": 1.0,
                            "family": "linear",
                            "inverted": False,
                            "label": "NLStdTomato",
                        },
                    ],
                    "id": 1,
                    "rdefs": {"defaultT": 0, "defaultZ": 92, "model": "color"},
                    "version": "0.4",
                },
                "_creator": {
                    "name": "omero-zarr",
                    "version": "0.5.6.dev59+g03d46b2.d20250610",
                },
            },
            members={
                "labels": GroupSpec(
                    zarr_format=2, attributes={"labels": ["0"]}, members={}
                ),
                "0": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 788, 1584),
                    chunks=(1, 1, 1024, 1024),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "1": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 394, 792),
                    chunks=(1, 1, 394, 792),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "2": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 197, 396),
                    chunks=(1, 1, 197, 396),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "3": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 98, 198),
                    chunks=(1, 1, 98, 198),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "4": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 49, 99),
                    chunks=(1, 1, 49, 99),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
                "5": ArraySpec(
                    zarr_format=2,
                    attributes={},
                    shape=(2, 184, 24, 49),
                    chunks=(1, 1, 24, 49),
                    dtype="|u1",
                    fill_value=0,
                    order="C",
                    filters=None,
                    dimension_separator="/",
                    compressor={
                        "id": "blosc",
                        "cname": "lz4",
                        "clevel": 5,
                        "shuffle": 1,
                        "blocksize": 0,
                    },
                ),
            },
        ),
    }
