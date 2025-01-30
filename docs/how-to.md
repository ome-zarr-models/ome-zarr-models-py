# How do I...?

## Validate an OME-Zarr group

If you know what type of group it is, use the `from_zarr()` method on [one of the group objects](api/index.md):

```python
import zarr
import ome_zarr_models.v04

zarr_group = zarr.open(path_to_group, mode="r")
hcs_group = ome_zarr_models.v04.HCS.from_zarr(zarr_group)
```

If you don't know what type of group it is, use `open_ome_zarr()`:

```python
import zarr
import ome_zarr_models.v04

zarr_group = zarr.open(path_to_group, mode="r")
ome_group = ome_zarr_models.open_ome_zarr(zarr_group)
```

If there aren't any errors, the Zarr group is a valid OME-Zarr group.
