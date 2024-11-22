from typing import Any


def get_path(store: Any) -> str:
    """
    Get a path from a zarr store
    """
    if hasattr(store, "path"):
        return store.path

    return ""


