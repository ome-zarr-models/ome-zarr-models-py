from pydantic import Field, field_validator

from ome_zarr_models.base import Base
from ome_zarr_models.utils import _unique_items_validator


class ImageInWell(Base):
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


class Well(Base):
    """
    Model for `NgffWellMeta.well`.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    images: list[ImageInWell] = Field(
        ..., description="The images included in this well", min_length=1
    )
    version: str | None = Field(None, description="The version of the specification")
    _check_unique = field_validator("images")(_unique_items_validator)


class NgffWellMeta(Base):
    """
    Model for the metadata of a NGFF well.

    See https://ngff.openmicroscopy.org/0.4/#well-md.
    """

    well: Well | None = None

    def get_acquisition_paths(self) -> dict[int, list[str]]:
        """
        Create mapping from acquisition indices to corresponding paths.

        Runs on the well zarr attributes and loads the relative paths in the
        well.

        Returns
        -------
            Dictionary with `(acquisition index: [image_path])` key/value
            pairs.

        Raises
        ------
            ValueError:
                If an element of `self.well.images` has no `acquisition`
                    attribute.
        """
        acquisition_dict = {}
        for image in self.well.images:
            if image.acquisition is None:
                raise ValueError(
                    "Cannot get acquisition paths for Zarr files without "
                    "'acquisition' metadata at the well level"
                )
            if image.acquisition not in acquisition_dict:
                acquisition_dict[image.acquisition] = []
            acquisition_dict[image.acquisition].append(image.path)
        return acquisition_dict
