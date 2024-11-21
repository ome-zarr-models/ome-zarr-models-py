""""""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ome_zarr_models")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"
