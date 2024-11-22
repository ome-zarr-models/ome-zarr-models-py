# Define the two types of OME-zarr dataset in this namespace
from ome_zarr_models.v04.hcs import HCS
from ome_zarr_models.v04.image import Image

__all__ = ["HCS", "Image"]
