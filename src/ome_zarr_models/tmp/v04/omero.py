from pydantic import BaseModel
from ome_zarr_models.base import Base


class Window(Base):
    """
    Model for `Channel.window`.

    See https://ngff.openmicroscopy.org/0.4/#omero-md.
    """

    max: float
    min: float
    start: float
    end: float


class Channel(Base):
    """
    Model for an element of `Omero.channels`.

    See https://ngff.openmicroscopy.org/0.4/#omero-md.
    """

    window: Window | None = None
    label: str | None = None
    family: str | None = None
    color: str
    active: bool | None = None


class Omero(BaseModel):
    """
    Model for `NgffImageMeta.omero`.

    See https://ngff.openmicroscopy.org/0.4/#omero-md.
    """

    channels: list[Channel]