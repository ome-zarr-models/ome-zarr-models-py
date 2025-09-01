from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Never, TypeVar

import pytest
import zarr
import zarr.storage
from zarr.abc.store import Store
from zarr.storage import LocalStore, MemoryStore

from ome_zarr_models.base import BaseAttrs

if TYPE_CHECKING:
    from zarr.abc.store import Store


T = TypeVar("T", bound=BaseAttrs)

EXAMPLES_PATH = Path(__file__).parent / "data" / "examples"
Version = Literal["0.4", "0.5", "0.6"]


def get_examples_path(*, version: Version) -> Path:
    """
    Get path to directory with example data.
    """
    if version == "0.4":
        return EXAMPLES_PATH / "v04"
    elif version == "0.5":
        return EXAMPLES_PATH / "v05"
    elif version == "0.6":
        return EXAMPLES_PATH / "v06"
    else:
        raise ValueError(f"Unknown value for {version=}")


def json_to_dict(*, version: Version, json_fname: str) -> Any:
    """
    Load an example JSON file and return as a dictionary.
    """
    with open(get_examples_path(version=version) / json_fname) as f:
        return json.load(f)


def read_in_json(*, version: Version, json_fname: str, model_cls: type[T]) -> T:
    """
    Load an example JSON file into a ome-zarr-models base attributes class.
    """
    with open(get_examples_path(version=version) / json_fname) as f:
        return model_cls.model_validate_json(f.read())


def json_to_zarr_group(
    *, version: Version, json_fname: str, store: Store
) -> zarr.Group:
    """
    Create an empty Zarr group, and set the attributes from an example JSON file.
    """
    zarr_format: Literal[2, 3]
    if version == "0.4":
        zarr_format = 2
    elif version in ["0.5", "0.6"]:
        zarr_format = 3
    else:
        raise ValueError(f"Unknown value for {version=}")
    group = zarr.open_group(store=store, zarr_format=zarr_format)
    with open(get_examples_path(version=version) / json_fname) as f:
        attrs = json.load(f)

    group.attrs.put(attrs)
    return group


class UnlistableStore(MemoryStore):
    """
    A memory store that doesn't support listing.

    Mimics other remote stores (e.g., HTTP) that don't support listing.
    """

    supports_listing: bool = False

    def list(self) -> Never:
        raise NotImplementedError

    def list_dir(self, prefix: str) -> Never:
        raise NotImplementedError

    def list_prefix(self, prefix: str) -> Never:
        raise NotImplementedError


@pytest.fixture(params=["MemoryStore", "LocalStore", "UnlistableStore"])
def store(request: pytest.FixtureRequest, tmp_path: Path) -> Store:
    match request.param:
        case "MemoryStore":
            return MemoryStore()
        case "LocalStore":
            return LocalStore(root=tmp_path)
        case "UnlistableStore":
            return UnlistableStore()
        case _:
            raise RuntimeError(f"Unknown store class: {request.param}")
