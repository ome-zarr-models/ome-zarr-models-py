from ome_zarr_models.zarr_models.base import FrozenBase


class Axis(FrozenBase):
    """
    Model for an element of `Multiscale.axes`.

    See https://ngff.openmicroscopy.org/0.4/#axes-md.
    """

    name: str
    type: str | None = None
    unit: str | None = None