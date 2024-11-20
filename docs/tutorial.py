# # Tutorial

from ome_zarr_models.v04 import Image as OMEZarrImage

my_image = OMEZarrImage(path="path/to/ome/zarr/directory.ome.zarr")
print(my_image.multiscales)
