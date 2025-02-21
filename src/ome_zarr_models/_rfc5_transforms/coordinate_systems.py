from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.axes import Axes


class CoordinateSystem(BaseAttrs):
    name: str
    axes: Axes
