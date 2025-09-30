from typing import TYPE_CHECKING

import zarr

from ome_zarr_models.common.omero import Channel, Omero, Window
from ome_zarr_models.v04.axes import Axis
from ome_zarr_models.v04.coordinate_transformations import VectorScale
from ome_zarr_models.v04.hcs import HCS, HCSAttrs
from ome_zarr_models.v04.image import ImageAttrs
from ome_zarr_models.v04.multiscales import Dataset, Multiscale
from ome_zarr_models.v04.plate import Acquisition, Column, Plate, Row, WellInPlate
from ome_zarr_models.v04.well_types import WellImage, WellMeta
from tests.conftest import get_examples_path

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_example_hcs() -> None:
    group = zarr.open_group(
        get_examples_path(version="0.4") / "hcs_example.ome.zarr",
        mode="r",
        zarr_format=2,
    )
    hcs: HCS = HCS.from_zarr(group)
    assert hcs.attributes == HCSAttrs(
        plate=Plate(
            acquisitions=[
                Acquisition(
                    id=0,
                    name="20200812-CardiomyocyteDifferentiation14-Cycle1",
                    maximumfieldcount=None,
                    description=None,
                    starttime=None,
                    endtime=None,
                )
            ],
            columns=[Column(name="03")],
            field_count=None,
            name=None,
            rows=[Row(name="B")],
            version="0.4",
            wells=[WellInPlate(path="B/03", rowIndex=0, columnIndex=0)],
        )
    )
    assert hcs.members is not None
    assert list(hcs.members.keys()) == ["B"]

    well_groups = list(hcs.well_groups)
    assert len(well_groups) == 1
    well_group = hcs.get_well_group(0)
    assert well_group.attributes.well == WellMeta(
        images=[WellImage(path="0", acquisition=None)], version="0.4"
    )

    images = list(well_group.images)
    assert len(images) == 1

    assert images[0].attributes == ImageAttrs(
        multiscales=[
            Multiscale(
                axes=[
                    Axis(name="c", type="channel", unit=None),
                    Axis(name="z", type="space", unit="micrometer"),
                    Axis(name="y", type="space", unit="micrometer"),
                    Axis(name="x", type="space", unit="micrometer"),
                ],
                datasets=[
                    Dataset(
                        path="0",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 0.1625, 0.1625]),
                        ),
                    ),
                    Dataset(
                        path="1",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 0.325, 0.325]),
                        ),
                    ),
                    Dataset(
                        path="2",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 0.65, 0.65]),
                        ),
                    ),
                    Dataset(
                        path="3",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 1.3, 1.3]),
                        ),
                    ),
                    Dataset(
                        path="4",
                        coordinateTransformations=(
                            VectorScale(type="scale", scale=[1.0, 1.0, 2.6, 2.6]),
                        ),
                    ),
                ],
                version="0.4",
                coordinateTransformations=None,
                metadata=None,
                name=None,
                type=None,
            )
        ],
        omero=Omero(
            channels=[
                Channel(
                    color="00FFFF",
                    window=Window(max=65535.0, min=0.0, start=110.0, end=800.0),
                    label="DAPI",
                    wavelength_id="A01_C01",
                )
            ],
            id=1,
            name="TBD",
            version="0.4",
        ),
    )


def test_non_existent_wells() -> None:
    """
    Make sure it's possible to create a HCS that has well paths that don't exist
    as Zarr groups.

    The relevant part of the OME-Zarr specification (https://ngff.openmicroscopy.org/0.4/index.html#plate-md)
    does not specify explicitly that the Zarr groups have to exist.
    """
    HCS(
        attributes={
            "plate": {
                "acquisitions": [{"id": 1}, {"id": 2}, {"id": 3}],
                "columns": [{"name": "1"}],
                "field_count": 10,
                "rows": [{"name": "A"}],
                "version": "0.4",
                "wells": [{"columnIndex": 0, "path": "A/1", "rowIndex": 0}],
            }
        }
    )


def test_non_existent_wells_from_zarr() -> None:
    """
    Same as above, but using from_zarr(...)
    """
    plate: dict[str, JsonValue] = {
        "columns": [{"name": "1"}],
        "rows": [{"name": "A"}],
        "wells": [{"path": "A/1", "rowIndex": 0, "columnIndex": 0}],
        "version": "0.4",
    }
    group = group = zarr.create_group(
        store={},
        zarr_format=2,
        attributes={"plate": plate, "version": "0.4"},
    )
    HCS.from_zarr(group)
