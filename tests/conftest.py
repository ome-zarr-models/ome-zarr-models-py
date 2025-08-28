from __future__ import annotations

from typing import TYPE_CHECKING, Never

import pytest
from zarr.storage import LocalStore, MemoryStore

if TYPE_CHECKING:
    from pathlib import Path

    from zarr.abc.store import Store


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
