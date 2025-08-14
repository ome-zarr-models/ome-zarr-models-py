from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from zarr.storage import LocalStore, MemoryStore

if TYPE_CHECKING:
    from pathlib import Path

    from zarr.abc.store import Store


@pytest.fixture(params=["MemoryStore", "LocalStore"])
def store(request: pytest.FixtureRequest, tmp_path: Path) -> Store:
    match request.param:
        case "MemoryStore":
            return MemoryStore()
        case "LocalStore":
            return LocalStore(root=tmp_path)
        case _:
            raise RuntimeError(f"Unknown store class: {request.param}")
