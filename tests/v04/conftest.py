

from dataclasses import replace
from typing import Any
from ome_zarr_models.v04.image import Axis
import pytest
from tests.conftest import fetch_schemas

@pytest.fixture
def image_schema(request: pytest.FixtureRequest) -> str:
    match request.param:
        case "strict":
            return fetch_schemas(
                version="0.4", 
                schema_name="image", 
                strict=True)
        case "relaxed":
            return fetch_schemas(
                version="0.4", 
                schema_name="image", 
                strict=False)
        case _:
            raise ValueError(f"Unknown schema type {request.param}")

ax_x = Axis(name='x', type='space', unit='meter')
ax_y = Axis(name='y', type='space', unit='meter')
ax_z = Axis(name='z', type='space', unit='meter')    
ax_t = Axis(name='t', type='time', unit='second')
ax_c = Axis(name='c', type='channel')
ax_w = Axis(name='?', type='custom')

@pytest.fixture
def recommended_axes(request: pytest.FixtureRequest) -> tuple[Axis, ...]:
    match request.param:
        case 'yx':
            return (ax_y, ax_x)
        case 'zyx': 
            return (ax_z, ax_y, ax_x)
        case 'czyx':
            return (ax_c, ax_z, ax_y, ax_x)
        case 'txyz':
            return (ax_c, ax_x, ax_y, ax_z)
        case 'tcxyz':
            return (ax_t, ax_c, ax_x, ax_y, ax_z)
        case 'ctxyz':
            return (ax_c, ax_t, ax_x, ax_y, ax_z)
        case 'wtzyx':
            return (ax_w, ax_t, ax_z, ax_y, ax_x)

@pytest.fixture
def disallowed_axes(request: pytest.FixtureRequest) -> tuple[Axis, ...]:
    match request.param:
        case 'x':
            # 1D data
            return (ax_x,)
        case 'xx':
            # duplicate axis name
            return (ax_x, ax_x)
        case 'xyza': 
            # 4 spatial axes
            return (ax_x, ax_y, ax_z, replace(ax_x, name='foo'))
        case 'xyzt':
            # incorrect axis order: time last
            return (ax_t, ax_x, ax_y, ax_z)
        case 'txyz':
            # incorrect axis order: channel first
            return (ax_c, ax_x, ax_y, ax_z)
        case 'wxyz':
            # incorrect axis order: custom first
            return (ax_w, ax_x, ax_y, ax_z)
        case 'xytt':
            # two time axes
            return (ax_x, ax_y, ax_t, replace(ax_t, name='foo'))
        case 'xycc':
            # two channel axes
            return (ax_x, ax_y, ax_c, replace(ax_c, name='foo'))
        case 'xyww':
            # two custom axes
            return (ax_x, ax_y, ax_z, ax_w, replace(ax_x, name='bar', type='custom'))