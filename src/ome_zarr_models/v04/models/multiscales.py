from ome_zarr_models.zarr_models.base import FrozenBase
from ome_zarr_models.zarr_models.utils import unique_items_validator
from ome_zarr_models.v04.v04.axes import Axis
from ome_zarr_models.v04.models.coordinate_transformations import PathScale, PathTranslation, VectorScale, VectorTranslation


from pydantic import Field, field_validator

from ome_zarr_models.v04.models.omero import Omero


class Dataset(FrozenBase):
    """
    Model for an element of `Multiscale.datasets`.

    See https://ngff.openmicroscopy.org/0.4/#multiscale-md
    """
    # TODO: validate that path resolves to an actual zarr array 
    path: str
    # TODO: validate that transforms are consistent w.r.t dimensionality
    coordinateTransformations: tuple[VectorScale | PathScale] | tuple[VectorScale | PathScale, VectorTranslation | PathTranslation]


class Multiscale(FrozenBase):
    """
    Model for an element of `NgffImageMeta.multiscales`.

    See https://ngff.openmicroscopy.org/0.4/#multiscale-md.
    """

    name: str | None = None
    datasets: list[Dataset] = Field(..., min_length=1)
    version: str | None = None
    axes: list[Axis] = Field(..., max_length=5, min_length=2)
    coordinateTransformations: Optional[
        list[
            Union[
                PathScale,
                VectorTranslation,
            ]
        ]
    ] = None
    _check_unique = field_validator("axes")(unique_items_validator)

    @field_validator("coordinateTransformations", mode="after")
    @classmethod
    def _no_global_coordinateTransformations(
        cls, v: list | None
    ) -> list | None:
        """
        Fail if Multiscale has a (global) coordinateTransformations attribute.
        """
        if v is None:
            return v
        else:
            raise NotImplementedError(
                "Global coordinateTransformations at the multiscales "
                "level are not currently supported in the fractal-tasks-core "
                "model for the NGFF multiscale."
            )


class MultiscaleGroupAttrs(FrozenBase):
    """
    Model for the metadata of a NGFF image.

    See https://ngff.openmicroscopy.org/0.4/#image-layout.
    """

    multiscales: list[Multiscale] = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )
    omero: Omero | None = None
    _check_unique = field_validator("multiscales")(unique_items_validator)