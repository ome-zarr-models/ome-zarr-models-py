from typing import Literal

from ome_zarr_models.base import Base

AxisType = Literal["space", "time", "channel"]


class Axis(Base):
    """
    Model for an element of `Multiscale.axes`.

    See https://ngff.openmicroscopy.org/0.4/#axes-md.
    """

    name: str
    type: str | None = None
    unit: str | None = None
