import zarr

from ome_zarr_models.exceptions import ValidationError
from ome_zarr_models.v04.multiscales import Multiscale, MultiscaleGroupAttrs
from ome_zarr_models.v04.omero import Omero

__all__ = ["Image"]


class Image:
    """
    A object representing OME-zarr image.

    Parameters
    ----------
    group :
        zarr Group which contains the image.
    """

    def __init__(self, group: zarr.Group):
        self._attrs = MultiscaleGroupAttrs(**group.attrs.asdict())
        if "labels" in group:
            if not isinstance(group["labels"], zarr.Group):
                raise ValidationError("The special group 'labels' is not a zarr group")

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

    @property
    def labels(self) -> list[str] | None:
        """
        Paths to labels that can be found in the special 'labels' group.
        """
