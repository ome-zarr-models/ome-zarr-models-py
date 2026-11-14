from typing import Any, Literal

import pydantic_zarr.v2
import pydantic_zarr.v3
import pytest
import zarr
import zarr.storage

import ome_zarr_models._pydantic_zarr_compat as pzc

# A user attribute that shares its name with zarr-python's consolidated
# metadata record, which the readers drop from a group's own metadata.
ATTRIBUTES = {"consolidated_metadata": {"user": "value"}, "other": 1}


# zarr-python warns that consolidated metadata is not part of the V3 spec
@pytest.mark.filterwarnings("ignore:Consolidated metadata is currently not part")
@pytest.mark.parametrize("zarr_format", [2, 3])
@pytest.mark.parametrize("consolidated", [False, True])
@pytest.mark.parametrize("depth", ["shallow", "full"])
def test_read_group(
    zarr_format: Literal[2, 3],
    consolidated: bool,
    depth: Literal["shallow", "full"],
) -> None:
    """
    Group readers keep every user attribute, including one named
    ``consolidated_metadata``, and drop zarr-python's consolidated record.
    """
    store = zarr.storage.MemoryStore()
    group = zarr.create_group(store, zarr_format=zarr_format, attributes=ATTRIBUTES)
    group.create_array("array", shape=(4,), dtype="uint8")
    if consolidated:
        zarr.consolidate_metadata(store, zarr_format=zarr_format)
    group = zarr.open_group(
        store, mode="r", zarr_format=zarr_format, use_consolidated=consolidated
    )

    spec: Any
    if depth == "shallow":
        spec = (
            pzc.read_group_shallow_v2(group)
            if zarr_format == 2
            else pzc.read_group_shallow_v3(group)
        )
    else:
        spec = (
            pzc.read_group_v2(pydantic_zarr.v2.GroupSpec, group)
            if zarr_format == 2
            else pzc.read_group_v3(pydantic_zarr.v3.GroupSpec, group)
        )
        assert set(spec.members) == {"array"}

    assert spec.attributes == ATTRIBUTES
    assert "consolidated_metadata" not in spec.model_dump(exclude={"attributes"})
