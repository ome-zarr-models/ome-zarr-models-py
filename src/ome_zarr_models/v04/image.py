import zarr

from ome_zarr_models.v04.multiscales import Multiscale, MultiscaleGroupAttrs
from ome_zarr_models.v04.omero import Omero

__all__ = ["Image"]


class Image:
    """
    A object representing OME-zarr image.

    Attributes
    ----------
    group :
        zarr group for the image.
    """

    def __init__(self, group: zarr.Group):
        self.group = group
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

    def save_attrs(self) -> None:
        """
        Put the current metadata in this object into the zarr Group.
        """
        self.group.attrs.put(self._attrs.model_dump_json())
