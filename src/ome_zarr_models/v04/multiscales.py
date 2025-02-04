"""
For reference, see the [multiscales section of the OME-Zarr specification](https://ngff.openmicroscopy.org/0.4/#multiscale-md).
"""

from ome_zarr_models.common.multiscales import Dataset, MultiscaleBase

__all__ = ["Dataset", "Multiscale"]


class Multiscale(MultiscaleBase):
    """
    An element of multiscales metadata.
    """

    pass
