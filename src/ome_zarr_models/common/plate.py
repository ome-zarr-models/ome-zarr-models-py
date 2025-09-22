from collections import Counter
from typing import Annotated, Self, TypeVar

from pydantic import (
    Field,
    NonNegativeInt,
    PositiveInt,
    field_validator,
    model_validator,
)

from ome_zarr_models.base import BaseAttrs
from ome_zarr_models.common.validation import (
    AlphaNumericConstraint,
    unique_items_validator,
)

__all__ = [
    "Acquisition",
    "Column",
    "PlateBase",
    "Row",
    "WellInPlate",
]

T = TypeVar("T")


class Acquisition(BaseAttrs):
    """
    A single acquisition.
    """

    id: NonNegativeInt = Field(description="A unique identifier.")
    name: str | None = None
    maximumfieldcount: PositiveInt | None = Field(
        default=None,
        description="Maximum number of fields of view for the acquisition",
    )
    description: str | None = None
    starttime: int | None = Field(
        default=None, description="Integer epoch timestamp of acquisition start time"
    )
    endtime: int | None = Field(
        default=None, description="Integer epoch timestamp of acquisition end time"
    )


class WellInPlate(BaseAttrs):
    """
    A single well within a plate.
    """

    # TODO: validate
    # path must be "{name in rows}/{name in columns}"
    path: str
    rowIndex: int
    columnIndex: int


class Column(BaseAttrs):
    """
    A single column within a well.
    """

    name: Annotated[str, AlphaNumericConstraint]


class Row(BaseAttrs):
    """
    A single row within a well.
    """

    name: Annotated[str, AlphaNumericConstraint]


class PlateBase(BaseAttrs):
    """
    A single plate.
    """

    acquisitions: list[Acquisition] | None = None
    columns: list[Column]
    field_count: PositiveInt | None = Field(
        default=None, description="Maximum number of fields per view across wells"
    )
    name: str | None = Field(default=None, description="Plate name")
    rows: list[Row]
    wells: list[WellInPlate]

    @field_validator("columns", "rows", mode="after")
    def _check_unique_items(cls, value: list[T]) -> list[T]:
        unique_items_validator(value)
        return value

    @model_validator(mode="after")
    def _check_well_paths(self) -> Self:
        """
        Check well paths are valid.
        """
        errors = []
        row_names = {row.name for row in self.rows}
        column_names = {column.name for column in self.columns}

        for well in self.wells:
            path = well.path
            if Counter(path)["/"] != 1:
                errors.append(f"well path '{path}' does not contain a single '/'")
                continue

            row, column = path.split("/")
            if row not in row_names:
                errors.append(
                    f"row '{row}' in well path '{path}' is not in list of rows"
                )
            if column not in column_names:
                errors.append(
                    f"column '{column}' in well path '{path}' is not in list of columns"
                )

        if len(errors) > 0:
            errors_joined = "\n".join(errors)
            raise ValueError(f"Error validating plate metadata:\n{errors_joined}")

        return self
