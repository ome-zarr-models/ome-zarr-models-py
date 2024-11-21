from enum import Enum
from ome_zarr_models.base import Base

class AxisType(str, Enum):
    """
    String enum representing the three axis types (`space`, `time`, `channel`) defined in the specification.
    """

    space = "space"
    time = "time"
    channel = "channel"

class Axis(Base):
    """
    Model for an element of `Multiscale.axes`.

    See https://ngff.openmicroscopy.org/0.4/#axes-md.
    """

    name: str
    type: str | None = None
    unit: str | None = None
