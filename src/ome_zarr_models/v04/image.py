import zarr

from ome_zarr_models.v04.multiscales import Multiscale, MultiscaleGroupAttrs
from ome_zarr_models.v04.omero import Omero

__all__ = ["Image"]


class Image:
    """
    A object representing OME-zarr image.
    """

    def __init__(self, group: zarr.Group):
        self._attrs = MultiscaleGroupAttrs(**group.attrs.asdict())

    @property
    def multiscales(self) -> list[Multiscale]:
        """
        A list of multiscales metadata objects.
        """
        return self._attrs.multiscales

    @property
    def omero(self) -> Omero | None:
        """
        The omero metadata object.

        Returns `None` if no omero metadata is present in the OME-zarr image.
        """
        return self._attrs.omero
