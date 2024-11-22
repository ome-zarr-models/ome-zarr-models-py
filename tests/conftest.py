from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zarr.storage import BaseStore
import pytest
from zarr.storage import MemoryStore


@pytest.fixture
def store(request: pytest.FixtureRequest) -> BaseStore:
    match request.param:
        case "memory":
            return MemoryStore()
        case _:
            raise ValueError(f"Invalid store requested: {request.param}")
