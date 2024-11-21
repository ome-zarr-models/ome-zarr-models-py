
from dataclasses import asdict
from ome_zarr_models.v04.image import Axis, Channel, ChannelWindow, Dataset, MultiscaleGroupAttributes, MultiscaleMetadata, Omero, TranslationTransform, ScaleTransform
import pytest
import jsonschema

recommended_axes = ["yx", "zyx", "czyx", "txyz", "tcxyz", "ctxyz", "wtzyx"]

@pytest.mark.parametrize("image_schema", ["strict", "relaxed"], indirect=True)
@pytest.mark.parametrize("recommended_axes", recommended_axes, indirect=True)
def test_multiscalei(image_schema: str, recommended_axes: tuple[Axis, ...]) -> None:
    axes = recommended_axes
    tforms = [
        ScaleTransform(scale=[1] * len(axes)), 
        TranslationTransform(translation=[0] * len(axes))
    ]

    omero = Omero(
        channels=[
            Channel(
                label="foo",    
                family='foo',
                color='red',
                active=True,
                window=ChannelWindow(end=0,max=0, min=0,start=0))
                ])

    multi_meta = MultiscaleMetadata(
        axes=list(axes),
        datasets=[Dataset(path="path", coordinateTransformations=tforms)],
        coordinateTransformations=tforms,
        name='my name',
        version='0.4',
        metadata={'foo': 'bar'},
        type='gaussian') 
    multi_group_meta = MultiscaleGroupAttributes(multiscales=[multi_meta], omero=omero)
    jsonschema.validate(asdict(multi_group_meta), image_schema)