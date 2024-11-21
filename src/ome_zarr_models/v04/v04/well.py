from ome_zarr_models.zarr_models.base import FrozenBase
from ome_zarr_models.zarr_models.utils import unique_items_validator


from pydantic import Field, field_validator


class ImageInWell(FrozenBase):
    """
    Model for an element of `Well.images`.

    **Note 1:** The NGFF image is defined in a different model
    (`NgffImageMeta`), while the `Image` model only refere to an item of
    `Well.images`.

    **Note 2:** We deviate from NGFF specs, since we allow `path` to be an
    arbitrary string.
    TODO: include a check like `constr(regex=r'^[A-Za-z0-9]+$')`, through a
    Pydantic validator.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    acquisition: int | None = Field(
        None, description="A unique identifier within the context of the plate"
    )
    path: str = Field(..., description="The path for this field of view subgroup")


class Well(FrozenBase):
    """
    Model for `NgffWellMeta.well`.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    images: list[ImageInWell] = Field(
        ..., description="The images included in this well", min_length=1
    )
    version: str | None = Field(None, description="The version of the specification")
    _check_unique = field_validator("images")(unique_items_validator)


class NgffWellMeta(FrozenBase):
    """
    Model for the metadata of a NGFF well.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    well: Well | None = None

