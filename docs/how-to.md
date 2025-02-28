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

## Create a new OME-Zarr group

Use the `.new()` method on [one of the group objects](api/index.md) (currently only supported on `Image`):

```python
import ome_zarr_models.v04

image_group = ome_zarr_models.v04.Image.new(...)
```

## Save an OME-Zarr group

Use the `.to_zarr()` method on [one of the group objects](api/index.md):

```python
import ome_zarr_models.v04
import zarr

store = zarr.DirectoryStore(path=...)
my_image_group.to_zarr(store=store, path="/")
```
