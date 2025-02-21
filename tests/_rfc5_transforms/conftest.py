from pathlib import Path
from typing import TypeVar

from ome_zarr_models.base import BaseAttrs

T = TypeVar("T", bound=BaseAttrs)


def read_in_json(*, json_fname: str, model_cls: type[T]) -> T:
    with open(
        Path(__file__).parent
        / "data_rfc5"
        / "from_specification"
        / "transformations"
        / json_fname
    ) as f:
        return model_cls.model_validate_json(f.read())
