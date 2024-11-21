import zarr

from ome_zarr_models.v04.multiscales import Multiscale, MultiscaleGroupAttrs
from ome_zarr_models.v04.omero import Omero


class Image:
    def __init__(self, group: zarr.Group):
        self.group = group
        self._attrs = MultiscaleGroupAttrs(**group.attrs.asdict())

    @property
    def multiscales(self) -> list[Multiscale]:
        return self._attrs.multiscales

    @property
    def omero(self) -> Omero | None:
        return self._attrs.omero

    def save_attrs(self) -> None:
        self.group.attrs.put(self._attrs.model_dump_json())
