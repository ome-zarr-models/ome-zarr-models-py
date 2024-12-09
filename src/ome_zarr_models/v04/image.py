from __future__ import annotations

from typing import Annotated, Self

import zarr
import zarr.errors
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ome_zarr_models.base import Base
from ome_zarr_models.v04.image_label import ImageLabel
from ome_zarr_models.v04.multiscales import Multiscales
from ome_zarr_models.v04.omero import Omero

# Image is imported to the `ome_zarr_py.v04` namespace, so not
# listed here
__all__ = ["ImageAttrs"]


class ImageAttrs(Base):
    """
    Model for the metadata of OME-zarr data.

    See https://ngff.openmicroscopy.org/0.4/#image-layout.
    """

    multiscales: Multiscales = Field(
        ...,
        description="The multiscale datasets for this image",
        min_length=1,
    )
    omero: Omero | None = None
    image_labels: Annotated[ImageLabel | None, Field(..., alias="image-label")] = None

    # TODO: validate:
    # "image-label groups MUST also contain multiscales metadata and the two "datasets"
    #  series MUST have the same number of entries."


class Image(BaseModel):
    """
    A OME-zarr image.

    This is represented by a single zarr Group. To get the OME-zarr
    metadata, use the `.attributes` property.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    group: zarr.Group

    @property
    def attributes(self) -> ImageAttrs:
        """
        Metadata attributes.
        """
        return ImageAttrs(**self.group.attrs.asdict())

    # TODO: before enabling this setter, check which fields of ImageAttrs
    # we can change while still keeping a valid data structure
    # (e.g., we can't just add extra channels without modifying the zarr data)
    """
    @attributes.setter
    def attributes(self, attrs: ImageAttrs) -> None:
        if not isinstance(attrs, ImageAttrs):
            raise ValueError(
                f"attributes must by of type ImageAttrs (got type {type(attrs)})"
            )
        self.group.attrs.put(attrs.model_dump(exclude_none=True))
    """

    @model_validator(mode="after")
    def _check_multiscale_arrays(self) -> Self:
        """
        Check that all the arrays referenced by the `multiscales` metadata meet the
        following criteria:

            - they exist
            - they are not groups
            - they have dimensionality consistent with the number of axes defined in the
              metadata.
        """
        multiscales = self.attributes.multiscales

        for multiscale in multiscales:
            for dataset in multiscale.datasets:
                if dataset.path not in self.group:
                    msg = (
                        f"The multiscale metadata references an array that does not "
                        f"exist in this group: {dataset.path}"
                    )
                    raise ValueError(msg)

                arr = self.group[dataset.path]
                if isinstance(arr, zarr.Group):
                    msg = f"The node at {dataset.path} is a group, not an array."
                    raise ValueError(msg)

                if arr.ndim != multiscale.ndim:
                    msg = (
                        f"The multiscale metadata has {multiscale.ndim} axes "
                        "which does not match the dimensionality of the array "
                        f"found in this group at {dataset.path} ({arr.ndim}). "
                        "The number of axes must match the array dimensionality."
                    )
                    raise ValueError(msg)
        return self
