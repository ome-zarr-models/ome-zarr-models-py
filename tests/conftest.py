from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zarr.abc.store import Store
import pytest
from zarr.storage import MemoryStore


@pytest.fixture
def store(request: pytest.FixtureRequest) -> Store:
    match request.param:
        case "memory":
            return MemoryStore()
        case _:
            raise ValueError(f"Invalid store requested: {request.param}")
